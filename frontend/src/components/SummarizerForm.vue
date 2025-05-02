<template>
  <div class="space-y-6">
    <!-- 输入框 -->
    <textarea
      v-model="inputText"
      placeholder="Paste your text here (multiple paragraphs supported)..."
      class="w-full h-40 p-4 border rounded"
    />

    <!-- 按钮 -->
    <button
      @click="summarize"
      :disabled="loading || !inputText.trim()"
      class="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700"
    >
      {{ loading ? "Summarizing..." : "Summarize" }}
    </button>

    <!-- 错误提示 -->
    <div v-if="error" class="text-red-600 font-bold">❌ {{ error }}</div>

    <!-- 结果展示 -->
    <div v-if="result?.hierarchy" class="space-y-6 mt-6">
      <div
        v-for="(level, levelIdx) in result.hierarchy"
        :key="'level-' + levelIdx"
        class="bg-white border border-gray-300 rounded-lg p-4 shadow"
      >
        <h3 class="text-lg font-semibold text-indigo-700 mb-2">
          🔷 Level {{ levelIdx + 1 }} {{ level.length === 1 ? 'Summary' : 'Summary Blocks' }}
        </h3>
        <ul class="list-disc ml-5 space-y-1 text-gray-800">
          <li v-for="(block, blockIdx) in level" :key="'block-' + blockIdx">
            {{ block }}
          </li>
        </ul>
      </div>

      <!-- Final summary 展示 -->
      <div class="bg-green-100 border border-green-500 p-4 rounded shadow mt-4">
        <h2 class="text-xl font-bold mb-2">✅ Final Summary (Level {{ result.depth + 1 }})</h2>
        <p class="whitespace-pre-line text-gray-800">{{ result.summary }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const inputText = ref('')
const result = ref(null)
const loading = ref(false)
const error = ref(null)

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
</script>
