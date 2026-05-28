<template>
  <div class="captcha-input">
    <div class="captcha-wrapper">
      <el-input
        v-model="inputValue"
        placeholder="请输入验证码"
        maxlength="6"
        @input="handleInput"
        ref="inputRef"
      />
      <div class="captcha-image" @click="refreshCaptcha">
        <span v-for="(letter, index) in captchaLetters" 
          :key="index" 
          :style="letter.style"
        >
          {{ letter.value }}
        </span>
      </div>
    </div>
    <div class="captcha-tip" v-if="showError">
      验证码错误，请重新输入
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'verified'])

const inputValue = ref('')
const inputRef = ref(null)
const captchaLetters = ref([])
const showError = ref(false)

// 生成随机字母
const generateCaptcha = () => {
  const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
  let code = ''
  const newLetters = []
  
  for (let i = 0; i < 6; i++) {
    const letter = letters.charAt(Math.floor(Math.random() * letters.length))
    code += letter
    newLetters.push({
      value: letter,
      style: {
        transform: `rotate(${Math.random() * 20 - 10}deg)`,
        color: `hsl(${Math.floor(Math.random() * 360)}, 70%, 40%)`,
        fontSize: `${Math.random() * 4 + 18}px`,
        fontWeight: Math.random() > 0.5 ? 'bold' : 'normal',
        textShadow: '1px 1px 2px rgba(0,0,0,0.2)',
        margin: '0 2px'
      }
    })
  }
  
  captchaLetters.value = newLetters
  return code
}

// 刷新验证码
const refreshCaptcha = () => {
  const code = generateCaptcha()
  inputValue.value = ''
  emit('update:modelValue', '')
  showError.value = false
  return code
}

// 处理输入
const handleInput = () => {
  emit('update:modelValue', inputValue.value)
  showError.value = false
  
  if (inputValue.value.length === 6) {
    const currentCode = captchaLetters.value.map(l => l.value).join('')
    if (inputValue.value.toUpperCase() === currentCode) {
      showError.value = false
      emit('verified', true)
    } else {
      showError.value = true
      inputValue.value = ''
      emit('update:modelValue', '')
      emit('verified', false)
      // 聚焦输入框
      inputRef.value?.input?.focus()
    }
  }
}

onMounted(() => {
  refreshCaptcha()
})
</script>

<style scoped>
.captcha-input {
  width: 100%;
}

.captcha-wrapper {
  display: flex;
  gap: 12px;
  align-items: stretch;
}

.captcha-image {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 120px;
  padding: 0 12px;
  background: #f5f7f9;
  border: 1px solid #dcdfe6;
  border-radius: 12px;
  cursor: pointer;
  user-select: none;
  transition: all 0.3s;
}

.captcha-image:hover {
  background: #e8f0fe;
  border-color: #4e6ef2;
}

.captcha-tip {
  font-size: 12px;
  color: #f56c6c;
  margin-top: 4px;
  padding-left: 12px;
}

:deep(.el-input__wrapper) {
  height: 48px;
  border-radius: 12px;
}
</style> 