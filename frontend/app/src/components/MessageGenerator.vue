<template>
  <el-card class="box-card">
    <template #header>
      <div class="card-header">
        <span>AI Message Generator</span>
        <el-text size="small" type="info">
          Generate tweakable messages from a prompt
        </el-text>
      </div>
    </template>

    <div class="generator-content">
      <el-input
        v-model="userPrompt"
        :rows="3"
        type="textarea"
        placeholder="e.g., I am trying to send a diwali wish to my customers"
        class="mb-4"
        :disabled="isLoading"
      />

      <el-button
        type="primary"
        @click="handleGenerateMessage"
        :loading="isLoading"
        class="w-full"
      >
        {{ isLoading ? 'Generating...' : 'Generate Message' }}
      </el-Button>

      <div v-if="generatedMessage" class="mt-6">
        <el-divider />
        <p class="mb-2 font-semibold text-gray-700">Generated Message (you can edit below):</p>
        <el-input
          v-model="generatedMessage"
          :rows="6"
          type="textarea"
          placeholder="Generated message will appear here"
        />
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { ElMessage } from 'element-plus'; // For showing success/error notifications

// --- Reactive State ---
const userPrompt = ref('');
const generatedMessage = ref('');
const isLoading = ref(false);

// --- API Call Logic ---
const handleGenerateMessage = async () => {
  if (!userPrompt.value.trim()) {
    ElMessage.warning('Please enter a prompt.');
    return;
  }

  isLoading.value = true;
  generatedMessage.value = ''; // Clear previous message

  try {
    // IMPORTANT: Get the authentication token.
    // Replace this with how you store your auth token (e.g., from localStorage, Pinia, or Vuex).
    const authToken = localStorage.getItem('authToken');

    if (!authToken) {
      ElMessage.error('Authentication token not found. Please log in.');
      isLoading.value = false;
      return;
    }

    // The 'vue.config.js' file proxies '/api' to your backend.
    // This allows us to use a relative path here.
    const response = await axios.post(
      '/api/generate-message/',
      {
        user_prompt: userPrompt.value
      },
      {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      }
    );

    generatedMessage.value = response.data.generated_message;
    ElMessage.success('Message generated successfully!');

  } catch (error) {
    console.error('Error generating message:', error);
    const errorMessage = error.response?.data?.detail || 'An unexpected error occurred.';
    ElMessage.error(`Generation failed: ${errorMessage}`);
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.mb-4 {
  margin-bottom: 1rem;
}
.mt-6 {
  margin-top: 1.5rem;
}
.w-full {
  width: 100%;
}
.font-semibold {
  font-weight: 600;
}
.text-gray-700 {
  color: #4a5568;
}
</style>