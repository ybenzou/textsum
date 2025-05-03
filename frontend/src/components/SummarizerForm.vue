<template>
  <div class="space-y-6 max-w-5xl mx-auto p-6">
    <!-- 模型选择 -->
    <div class="space-y-2">
      <label class="block text-sm font-semibold text-gray-600">🧠 Select Model:</label>
      <select v-model="selectedModel" class="p-2 border rounded">
        <option v-for="model in models" :key="model" :value="model">{{ model }}</option>
      </select>
    </div>

    <!-- 上传 PDF -->
    <div class="space-y-2">
      <label class="block text-sm font-semibold text-gray-600">📄 Upload PDF:</label>
      <input type="file" accept="application/pdf" @change="handlePDFUpload" class="block" />
    </div>

    <!-- 输入框 -->
    <textarea
      v-model="inputText"
      placeholder="Paste your text here (multiple paragraphs supported)..."
      class="w-full h-40 p-4 border rounded resize-none text-gray-800"
    />

    <!-- 按钮 -->
    <button
      @click="summarize"
      :disabled="loading || !inputText.trim()"
      class="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
    >
      {{ loading ? "Summarizing..." : "Summarize" }}
    </button>

    <!-- 错误提示 -->
    <div v-if="error" class="text-red-600 font-bold">❌ {{ error }}</div>

    <!-- 展示结果 -->
    <div v-if="result?.hierarchy?.length" class="space-y-6 mt-6">
      <div class="bg-green-100 border border-green-500 p-4 rounded shadow">
        <h2 class="text-xl font-bold mb-2">✅ Final Summary (Level {{ result.depth }})</h2>
        <p class="whitespace-pre-line text-gray-800">{{ result.summary }}</p>
      </div>

      <div
        v-for="(level, index) in result.hierarchy.slice().reverse()"
        :key="'level-' + index"
        class="space-y-4"
      >
        <h3 class="text-xl font-semibold text-gray-800">
          🔷 Level {{ result.hierarchy.length - index }} {{ level.length === 1 ? 'Summary' : 'Summary Blocks' }}
        </h3>

        <ul class="space-y-6">
          <li
            v-for="(block, blockIdx) in level"
            :key="'block-' + blockIdx"
            class="bg-white border border-gray-200 p-5 rounded-xl shadow-sm"
          >
            <div class="text-gray-900 text-base leading-relaxed font-medium">
              {{ typeof block === 'string' ? block : block.text }}
            </div>

            <div
              v-if="typeof block !== 'string' && block.sources && (result.hierarchy.length - 1 - index) > 0"
              class="mt-4 space-y-2"
            >
              <p class="text-sm text-gray-500 font-semibold">Derived from:</p>
              <div class="space-y-2">
                <div
                  v-for="srcIdx in block.sources"
                  :key="'conn-' + srcIdx"
                  class="rounded-md bg-blue-50 border border-blue-200 px-3 py-2 text-sm text-blue-900 shadow-sm"
                >
                  {{ getPreviousSummary(result.hierarchy.length - 1 - index, srcIdx) }}
                </div>
              </div>
            </div>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import * as pdfjsLib from 'pdfjs-dist/legacy/build/pdf'
import Worker from 'pdfjs-dist/legacy/build/pdf.worker?worker'

pdfjsLib.GlobalWorkerOptions.workerPort = new Worker()

const inputText = ref('')
const result = ref(null)
const loading = ref(false)
const error = ref(null)
const selectedModel = ref('t5_small')
const models = ref([])

onMounted(async () => {
  try {
    const res = await axios.get('http://localhost:8000/models')
    models.value = res.data.models
    if (!selectedModel.value && models.value.length) {
      selectedModel.value = models.value[0]
    }
  } catch (err) {
    console.error('Failed to fetch model list:', err)
  }
})

async function handlePDFUpload(event) {
  const file = event.target.files[0]
  if (!file) return

  try {
    const reader = new FileReader()
    reader.onload = async function () {
      const typedArray = new Uint8Array(reader.result)
      const pdf = await pdfjsLib.getDocument({ data: typedArray }).promise
      let textContent = ''
      for (let i = 1; i <= pdf.numPages; i++) {
        const page = await pdf.getPage(i)
        const content = await page.getTextContent()
        textContent += content.items.map((item) => item.str).join(' ') + '\n\n'
      }
      inputText.value = textContent.trim()
    }
    reader.readAsArrayBuffer(file)
  } catch (err) {
    console.error('PDF extraction failed:', err)
    error.value = '❌ Failed to read PDF file.'
  }
}

async function summarize() {
  loading.value = true
  error.value = null
  result.value = null

  try {
    const res = await axios.post('http://localhost:8000/summarize_recursive', {
      text: inputText.value,
      model_name: selectedModel.value
    })
    result.value = res.data
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to summarize.'
  } finally {
    loading.value = false
  }
}

function getPreviousSummary(levelIdx, sourceIdx) {
  const prevLevel = result.value.hierarchy[levelIdx - 1]
  const src = prevLevel?.[sourceIdx]
  return typeof src === 'string' ? src : src?.text || '???'
}
</script>
