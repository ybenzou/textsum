<template>
  <div class="space-y-6 max-w-5xl mx-auto p-6">
    <!-- 上传 PDF -->
    <div class="space-y-2">
      <label class="block text-sm font-semibold text-gray-600">📄 Upload PDF:</label>
      <input
        type="file"
        accept="application/pdf"
        @change="handlePDFUpload"
        class="block"
      />
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
      <!-- Final summary -->
      <div class="bg-green-100 border border-green-500 p-4 rounded shadow">
        <h2 class="text-xl font-bold mb-2">✅ Final Summary (Level {{ result.depth + 1 }})</h2>
        <p class="whitespace-pre-line text-gray-800">{{ result.summary }}</p>
      </div>

      <!-- 倒序层级展示 -->
      <!-- 倒序层级展示 -->
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
            <!-- 当前摘要 -->
            <div class="text-gray-900 text-base leading-relaxed font-medium">
              {{ typeof block === 'string' ? block : block.text }}
            </div>

            <!-- 来源引用（简约风格） -->
            <div
              v-if="typeof block !== 'string' && block.sources && (result.hierarchy.length - 1 - index) > 0"
              class="mt-4 space-y-2"
            >
              <p class="text-sm text-gray-500 font-semibold">Derived from:</p>
              <div class="space-y-2">
                <div
                  v-for="srcIdx in block.sources"
                  :key="'conn-' + srcIdx"
                  class="rounded-md bg-gray-100 border border-gray-200 px-3 py-2 text-sm text-gray-700 shadow-sm"
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
import { ref } from 'vue'
import axios from 'axios'
import * as pdfjsLib from 'pdfjs-dist/legacy/build/pdf'
import Worker from 'pdfjs-dist/legacy/build/pdf.worker?worker'

// 设置 worker 运行时（仅 Vite）
pdfjsLib.GlobalWorkerOptions.workerPort = new Worker()



const inputText = ref('')
const result = ref(null)
const loading = ref(false)
const error = ref(null)

// PDF 上传处理
async function handlePDFUpload(event) {
  const file = event.target.files[0]
  if (!file) return

  try {
    const reader = new FileReader()
    reader.onload = async function () {
      const typedArray = new Uint8Array(reader.result)

      const pdf = await pdfjsLib.getDocument({ data: typedArray }).promise
      const maxPages = pdf.numPages
      let textContent = ''

      for (let i = 1; i <= maxPages; i++) {
        const page = await pdf.getPage(i)
        const content = await page.getTextContent()
        const strings = content.items.map((item) => item.str)
        textContent += strings.join(' ') + '\n\n'
      }

      inputText.value = textContent.trim()
    }

    reader.readAsArrayBuffer(file)
  } catch (err) {
    console.error('PDF extraction failed:', err)
    error.value = '❌ Failed to read PDF file.'
  }
}

// 发起摘要请求
async function summarize() {
  loading.value = true
  error.value = null
  result.value = null

  try {
    const res = await axios.post('http://localhost:8000/summarize_recursive', {
      text: inputText.value
    })
    result.value = res.data
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to summarize.'
  } finally {
    loading.value = false
  }
}

// 获取上一层摘要内容
function getPreviousSummary(levelIdx, sourceIdx) {
  const prevLevel = result.value.hierarchy[levelIdx - 1]
  const src = prevLevel?.[sourceIdx]
  return typeof src === 'string' ? src : src?.text || '???'
}
</script>
