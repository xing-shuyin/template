<template>
  <div class="chat-page">
    <!-- Sidebar -->
    <transition name="slide">
      <div v-if="sidebarOpen" class="chat-overlay" @click="sidebarOpen = false" />
    </transition>
    <aside class="chat-sidebar" :class="{ open: sidebarOpen }">
      <div class="sidebar-header">
        <div class="sidebar-brand">
          <span class="brand-icon">✦</span>
          <span>AI 对话</span>
        </div>
        <button class="btn-new" @click="newChat">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          新对话
        </button>
      </div>

      <div class="chat-list">
        <div v-for="c in chats" :key="c.id" class="chat-item"
          :class="{ active: currentChat?.id === c.id }"
          @click="switchChat(c)">
          <div class="chat-item-icon">💬</div>
          <span class="chat-item-name">{{ c.name || '新对话' }}</span>
          <button class="chat-item-del" @click.stop="deleteChat(c)" title="删除">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
          </button>
        </div>
        <div v-if="!chats.length" class="empty-tip">暂无对话</div>
      </div>

      <div class="sidebar-footer" v-if="models.length">
        <div class="model-select-wrapper">
          <svg class="model-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a4 4 0 0 1 4 4v2a4 4 0 0 1-8 0V6a4 4 0 0 1 4-4z"/><path d="M5 16v2a7 7 0 0 0 14 0v-2"/></svg>
          <select v-model="currentModel" class="model-select">
            <option v-for="m in models" :key="m.id" :value="m.id">{{ m.label || m.name }}</option>
          </select>
        </div>
      </div>
    </aside>

    <!-- Main -->
    <div class="chat-main">
      <!-- Header -->
      <header class="main-header">
        <button class="menu-btn" @click="sidebarOpen = !sidebarOpen" title="对话列表">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
        </button>
        <span class="header-title">{{ currentChat?.name || 'AI 智能助手' }}</span>
        <select v-if="models.length" v-model="currentModel" class="header-model-select">
          <option v-for="m in models" :key="m.id" :value="m.id">{{ m.label || m.name }}</option>
        </select>
      </header>

      <!-- Messages -->
      <div class="messages-area" ref="messagesRef" @scroll="onScroll">
        <div v-if="!messages.length" class="welcome">
          <div class="welcome-icon">✦</div>
          <div class="welcome-title">AI 智能助手</div>
          <div class="welcome-sub">您的智能对话伙伴，随时为您解答问题</div>
          <div class="welcome-suggestions">
            <div class="suggestion-chip" @click="quickSend('帮我总结一下今天的工作')">📋 总结工作</div>
            <div class="suggestion-chip" @click="quickSend('用专业的口吻改写这段话')">✏️ 改写润色</div>
            <div class="suggestion-chip" @click="quickSend('帮我写一个 Python 脚本')">💻 写代码</div>
            <div class="suggestion-chip" @click="quickSend('解释一下什么是 RESTful API')">📖 解释概念</div>
          </div>
        </div>

        <div class="messages-inner">
          <div v-for="(msg, i) in messages" :key="msg._id || i" class="msg-row"
            :class="msg.role === 'user' ? 'msg-user' : 'msg-ai'">
            <div class="msg-avatar" :class="msg.role">
              <span v-if="msg.role === 'user'">你</span>
              <span v-else>AI</span>
            </div>
            <div class="msg-body">
              <div class="msg-content">
                <template v-if="msg.role === 'user'">
                  <div class="msg-text" v-text="msg.content" />
                  <div v-if="msg.uploads?.length" class="msg-files">
                    <div v-for="f in msg.uploads" :key="f.id" class="file-chip" @click="downloadFile(f)">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                      {{ f.name }}
                    </div>
                  </div>
                </template>
                <template v-else>
                  <div class="msg-text markdown-body" v-html="renderMarkdown(msg)" />
                  <div v-if="i === messages.length - 1 && streaming" class="stream-indicator">
                    <span>●</span> 正在生成...
                  </div>
                </template>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Input -->
      <div class="input-area" :class="{ 'has-uploads': uploads.length }">
        <div class="input-box-container">
          <div class="input-box">
            <div v-if="uploads.length" class="uploads-list">
              <div v-for="f in uploads" :key="f.id" class="upload-item">
                <svg class="upload-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                <span class="upload-name">{{ f.name }}</span>
                <svg class="upload-close" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" @click="removeUpload(f)"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
              </div>
            </div>
            <textarea ref="textareaRef" v-model="inputText" class="input-textarea"
              placeholder="输入消息，Enter 发送，Shift+Enter 换行"
              @keydown="onKeydown" :disabled="streaming"
              @input="autoResizeTextarea" />
            <div class="input-btns">
              <div class="input-btns-left">
                <button class="input-btn" @click="triggerFileInput" title="上传文件">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/></svg>
                </button>
                <input ref="fileInputRef" type="file" class="file-input-hidden" multiple
                  accept=".txt,.json,.csv,.md,.pdf,.py,.js,.ts,.vue,.html,.css" @change="handleFileChange" />
              </div>
              <div class="input-btns-right">
                <button v-if="streaming" class="input-btn stop-btn" @click="stopStream" title="停止生成">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="6" width="12" height="12" rx="1"/></svg>
                </button>
                <button v-else class="send-btn" @click="sendMessage" :disabled="!inputText.trim()" title="发送">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import r from '@/utils/request'
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'

const md = new MarkdownIt({
  html: false, breaks: true, linkify: true,
  highlight(str, lang) {
    try {
      const code = lang && hljs.getLanguage(lang)
        ? hljs.highlight(str, { language: lang, ignoreIllegals: true }).value
        : hljs.highlightAuto(str).value
      return `<pre class="hljs code-block"><button class="copy-btn" onclick="navigator.clipboard.writeText(this.nextElementSibling.textContent)">复制</button><code>${code}</code></pre>`
    } catch {
      return `<pre class="hljs code-block"><code>${escapeHtml(str)}</code></pre>`
    }
  }
})
const escapeHtml = (s) => s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')

const renderMarkdown = (msg) => {
  let content = msg.content || ''
  if (msg.reason) return md.render(`::: details 思考过程\n${msg.reason}\n:::\n\n${content}`)
  return md.render(content)
}

/* ─── State ─── */
const textareaRef = ref(null)
const messagesRef = ref(null)
const fileInputRef = ref(null)
const sidebarOpen = ref(false)

const chats = ref([])
const currentChat = ref(null)
const messages = ref([])
const inputText = ref('')
const uploads = ref([])
const streaming = ref(false)
const models = ref([])
const currentModel = ref(null)
const autoScroll = ref(true)

let ws = null
let wsConnected = false

onMounted(() => { fetchModels() })
onUnmounted(() => { disconnectWs() })

/* ─── API ─── */
const fetchModels = async () => {
  try {
    const res = await r.get('/chat/models/')
    models.value = res.data.data || []
    if (models.value.length && !currentModel.value) currentModel.value = models.value[0].id
    fetchChats()
  } catch (e) { console.error(e) }
}

const fetchChats = async () => {
  try {
    const res = await r.get('/chat/', { params: { limit: 100, sort: '-created_at' } })
    chats.value = res.data.data || []
    if (chats.value.length && !currentChat.value) {
      currentChat.value = chats.value[0]
      fetchMessages(currentChat.value.id)
    }
  } catch (e) { console.error(e) }
}

const fetchMessages = async (id) => {
  try {
    const res = await r.get(`/chat/${id}`)
    currentChat.value = res.data
    messages.value = res.data.messages || []
    nextTick(scrollToBottom)
  } catch (e) { console.error(e) }
}

const newChat = () => {
  currentChat.value = null; messages.value = []
  inputText.value = ''; uploads.value = []; sidebarOpen.value = false
}

const switchChat = (chat) => {
  if (chat.id === currentChat.value?.id) return
  disconnectWs(); currentChat.value = chat
  fetchMessages(chat.id); sidebarOpen.value = false
}

const deleteChat = async (chat) => {
  try {
    await r.delete(`/chat/${chat.id}`)
    chats.value = chats.value.filter(c => c.id !== chat.id)
    if (currentChat.value?.id === chat.id) newChat()
    ElMessage({ message: '已删除', type: 'success' })
  } catch (e) { ElMessage({ message: '删除失败', type: 'error' }) }
}

const createChat = async (firstMsg) => {
  const name = typeof firstMsg === 'string' ? firstMsg.slice(0, 20) : '新对话'
  const res = await r.post('/chat/', { name, model: String(currentModel.value || ''), messages: [] })
  return res.data
}

const renameChat = async (id, name) => {
  await r.patch(`/chat/${id}`, { name: name.slice(0, 50) })
}

const quickSend = (text) => {
  inputText.value = text
  sendMessage()
}

/* ─── WebSocket ─── */
const getWsUrl = () => {
  const token = localStorage.getItem('access_token') || ''
  const wsUrl = import.meta.env.VITE_WS_URL
  if (wsUrl) return `${wsUrl.replace(/\/$/, '')}/chat/ws?token=${token}`
  const base = import.meta.env.VITE_BASE_API || '/'
  let wsBase
  if (base.startsWith('http')) {
    wsBase = base.replace(/^http/, 'ws')
  } else {
    wsBase = `${location.protocol === 'https:' ? 'wss:' : 'ws:'}//${location.host}${base}`
  }
  return `${wsBase.replace(/\/$/, '')}/chat/ws?token=${token}`
}

const connectWs = () => {
  if (wsConnected) return
  try {
    ws = new WebSocket(getWsUrl())
    ws.onopen = () => { wsConnected = true }
    ws.onclose = () => { wsConnected = false; ws = null }
    ws.onerror = () => { wsConnected = false }
    ws.onmessage = handleWsMessage
  } catch (e) { console.error(e) }
}

const disconnectWs = () => {
  if (ws) { ws.close(); ws = null; wsConnected = false }
}

const handleWsMessage = (event) => {
  let data
  try { data = JSON.parse(event.data) } catch { return }
  const last = messages.value[messages.value.length - 1]

  switch (data.type) {
    case 'delta':
      if (last && last.role === 'assistant') last.content = (last.content || '') + (data.content || '')
      break
    case 'reason':
      if (last && last.role === 'assistant') last.reason = (last.reason || '') + (data.content || '')
      break
    case 'tool_calls':
      messages.value.push({ role: 'assistant', tool_calls: data.data })
      break
    case 'end':
      streaming.value = false
      if (currentChat.value?.id && messages.value.length > 0) {
        const u = messages.value.find(m => m.role === 'user')
        if (u) {
          const n = typeof u.content === 'string' ? u.content.slice(0, 20) : '新对话'
          renameChat(currentChat.value.id, n)
          const c = chats.value.find(x => x.id === currentChat.value.id)
          if (c) c.name = n
        }
      }
      nextTick(scrollToBottom)
      break
    case 'cancelled': streaming.value = false; break
    case 'error':
      streaming.value = false
      ElMessage({ message: data.message || '请求出错', type: 'error' })
      break
  }
  nextTick(scrollToBottom)
}

/* ─── Send / Stop ─── */
const sendMessage = async () => {
  const text = inputText.value.trim()
  if (!text || streaming.value) return
  if (!currentModel.value && models.value.length) currentModel.value = models.value[0].id
  if (!currentChat.value?.id) {
    try {
      const created = await createChat(text)
      currentChat.value = created; chats.value.unshift(created)
    } catch (e) { ElMessage({ message: '创建对话失败', type: 'error' }); return }
  }
  messages.value.push({ role: 'user', content: text, uploads: [...uploads.value] })
  inputText.value = ''; uploads.value = []; autoScroll.value = true
  messages.value.push({ role: 'assistant', _id: Date.now(), content: '', reason: '' })
  streaming.value = true
  connectWs()
  if (!wsConnected) {
    await nextTick(); await new Promise(r => setTimeout(r, 500))
    if (!wsConnected) { streaming.value = false; ElMessage({ message: 'WebSocket 连接失败', type: 'error' }); return }
  }
  ws.send(JSON.stringify({
    action: 'send',
    messages: messages.value.filter(m => m.role !== 'assistant' || m.content || m.tool_calls)
      .map(m => ({ role: m.role, content: m.content || '', ...(m.uploads ? { uploads: m.uploads } : {}) })),
    model_id: currentModel.value, chat_id: currentChat.value.id,
  }))
  resetTextareaHeight()
}

const stopStream = () => {
  if (ws && wsConnected) ws.send(JSON.stringify({ action: 'stop' }))
  streaming.value = false
}

const onKeydown = (e) => {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage() }
}

/* ─── File Upload ─── */
const triggerFileInput = () => { fileInputRef.value?.click() }

const handleFileChange = async (e) => {
  const files = e.target.files
  if (!files?.length) return
  const fd = new FormData()
  for (const f of files) fd.append('files', f)
  try {
    const res = await r.post('/uploads/', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    const items = Array.isArray(res.data) ? res.data : (res.data?.data || [])
    uploads.value.push(...items)
  } catch (e) { ElMessage({ message: '上传失败', type: 'error' }) }
  if (fileInputRef.value) fileInputRef.value.value = ''
}

const removeUpload = (f) => { uploads.value = uploads.value.filter(x => x.id !== f.id) }

const downloadFile = (f) => {
  const base = import.meta.env.VITE_BASE_API || '/'
  const url = `${base.replace(/\/$/, '')}/download/${f.id}/`
  const a = document.createElement('a')
  a.href = url
  a.download = f.name || ''
  a.click()
}

/* ─── Textarea ─── */
const autoResizeTextarea = () => {
  const el = textareaRef.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 160) + 'px'
}

const resetTextareaHeight = () => {
  const el = textareaRef.value
  if (el) el.style.height = 'auto'
}

/* ─── Scroll ─── */
const scrollToBottom = () => {
  if (!autoScroll.value) return
  nextTick(() => { const el = messagesRef.value; if (el) el.scrollTop = el.scrollHeight })
}

const onScroll = () => {
  const el = messagesRef.value
  if (!el) return
  autoScroll.value = el.scrollHeight - el.scrollTop - el.clientHeight < 100
}
</script>

<style scoped>
.chat-page {
  display: flex;
  height: 100vh;
  background: var(--el-bg-color-page);
  color: var(--el-text-color-primary);
  overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

/* ─── Overlay ─── */
.chat-overlay {
  position: fixed;
  inset: 0;
  z-index: 99;
  background: rgba(0,0,0,0.3);
}
.slide-enter-active, .slide-leave-active { transition: opacity .25s; }

/* ─── Sidebar ─── */
.chat-sidebar {
  width: 280px;
  min-width: 280px;
  background: var(--el-bg-color);
  border-right: 1px solid var(--el-border-color-light);
  display: flex;
  flex-direction: column;
  z-index: 100;
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid var(--el-border-color-light);
}
.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 14px;
  color: var(--el-text-color-primary);
}
.brand-icon {
  width: 28px; height: 28px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 8px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  font-size: 14px;
}
.btn-new {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  width: 100%;
  padding: 9px 0;
  border: none;
  border-radius: 10px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity .2s, transform .15s;
}
.btn-new:hover { opacity: .9; transform: translateY(-1px); }
.btn-new:active { transform: translateY(0); }

.chat-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}
.chat-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 10px;
  cursor: pointer;
  margin-bottom: 2px;
  transition: background .15s;
  position: relative;
  group: true;
}
.chat-item:hover { background: var(--el-fill-color-light); }
.chat-item.active { background: var(--el-color-primary-light-9); }
.chat-item-icon { font-size: 16px; flex-shrink: 0; }
.chat-item-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 14px;
}
.chat-item-del {
  opacity: 0;
  border: none;
  background: none;
  cursor: pointer;
  color: var(--el-text-color-secondary);
  padding: 4px;
  border-radius: 6px;
  transition: opacity .15s, background .15s;
  flex-shrink: 0;
}
.chat-item:hover .chat-item-del { opacity: 1; }
.chat-item-del:hover { background: var(--el-fill-color-darker); color: var(--el-color-danger); }

.empty-tip {
  text-align: center;
  color: var(--el-text-color-secondary);
  padding: 32px 16px;
  font-size: 13px;
}

.sidebar-footer {
  padding: 12px 16px;
  border-top: 1px solid var(--el-border-color-light);
}
.model-select-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  border-radius: 8px;
  background: var(--el-fill-color-light);
}
.model-icon { flex-shrink: 0; opacity: .5; }
.model-select {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 13px;
  color: var(--el-text-color-primary);
  outline: none;
  appearance: none;
  cursor: pointer;
}

/* ─── Main ─── */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.main-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  border-bottom: 1px solid var(--el-border-color-light);
  background: var(--el-bg-color);
}
.menu-btn {
  display: none;
  border: none;
  background: none;
  cursor: pointer;
  color: var(--el-text-color-secondary);
  padding: 6px;
  border-radius: 8px;
  transition: background .15s;
}
.menu-btn:hover { background: var(--el-fill-color-light); }
.header-title {
  font-weight: 600;
  font-size: 15px;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.header-model-select {
  border: 1px solid var(--el-border-color);
  border-radius: 8px;
  padding: 6px 10px;
  font-size: 13px;
  background: var(--el-fill-color-blank);
  color: var(--el-text-color-primary);
  outline: none;
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23999' stroke-width='2'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 8px center;
  padding-right: 28px;
}

/* ─── Messages ─── */
.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 0 0 180px;
  scroll-behavior: smooth;
}
.messages-inner {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px 20px 16px;
}

.welcome {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px 40px;
  text-align: center;
}
.welcome-icon {
  width: 64px; height: 64px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 20px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  font-size: 28px;
  margin-bottom: 20px;
  box-shadow: 0 8px 24px rgba(99,102,241,0.3);
}
.welcome-title {
  font-size: 26px;
  font-weight: 800;
  background: linear-gradient(135deg, var(--el-color-primary), #8b5cf6);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  margin-bottom: 8px;
}
.welcome-sub {
  font-size: 15px;
  color: var(--el-text-color-secondary);
  margin-bottom: 28px;
}
.welcome-suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
  max-width: 500px;
}
.suggestion-chip {
  padding: 10px 18px;
  border-radius: 20px;
  background: var(--el-fill-color-light);
  border: 1px solid var(--el-border-color-light);
  font-size: 13px;
  cursor: pointer;
  transition: all .2s;
  user-select: none;
}
.suggestion-chip:hover {
  border-color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
  transform: translateY(-1px);
}

/* ─── Message Row ─── */
.msg-row {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  animation: msgIn .3s ease-out;
}
@keyframes msgIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}
.msg-row.msg-user { flex-direction: row-reverse; }

.msg-avatar {
  width: 34px; height: 34px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  flex-shrink: 0;
  margin-top: 4px;
}
.msg-avatar.user {
  background: linear-gradient(135deg, #6366f1, #4f46e5);
  color: #fff;
}
.msg-avatar.assistant {
  background: linear-gradient(135deg, #10b981, #059669);
  color: #fff;
}

.msg-body { max-width: 80%; min-width: 0; }
.msg-row.msg-user .msg-body { display: flex; flex-direction: column; align-items: flex-end; }

.msg-content {
  display: inline-block;
}
.msg-text {
  padding: 12px 18px;
  border-radius: 16px;
  font-size: 14px;
  line-height: 1.65;
  word-break: break-word;
}
.msg-row.msg-user .msg-text {
  background: linear-gradient(135deg, var(--el-color-primary-light-8), var(--el-color-primary-light-7));
  border-bottom-right-radius: 4px;
}
.msg-row.msg-ai .msg-text {
  background: var(--el-fill-color-light);
  border-bottom-left-radius: 4px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

/* ─── Files in Message ─── */
.msg-files {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
  justify-content: flex-end;
}
.file-chip {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 5px 10px;
  background: var(--el-fill-color);
  border-radius: 8px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
  cursor: pointer;
  transition: background .15s, color .15s;
}
.file-chip:hover {
  background: var(--el-color-primary-light-9);
  color: var(--el-color-primary);
}

/* ─── Streaming ─── */
.stream-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
  font-size: 12px;
  color: var(--el-color-primary);
  animation: pulse 1.5s ease-in-out infinite;
}
.stream-indicator span { font-size: 8px; animation: blink 1s steps(1) infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: .5; } }
@keyframes blink { 50% { opacity: 0; } }

/* ─── Input Area ─── */
.input-area {
  position: fixed;
  bottom: 0;
  left: 280px;
  right: 0;
  pointer-events: none;
  z-index: 10;
}
.input-box-container {
  max-width: 1068px;
  margin: 0 auto;
  padding: 0 20px 20px;
  pointer-events: none;
}
.input-box {
  width: 100%;
  min-height: 110px;
  max-height: 25dvh;
  border-radius: 24px;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-light);
  box-shadow: 0 4px 24px rgba(0,0,0,0.06);
  padding: 12px 16px 8px;
  display: flex;
  flex-direction: column;
  pointer-events: auto;
  transition: box-shadow .2s, border-color .2s;
}
.input-box:focus-within {
  border-color: var(--el-color-primary-light-5);
  box-shadow: 0 4px 24px rgba(99,102,241,0.1);
}

.uploads-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 6px;
}
.upload-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 10px;
  background: var(--el-fill-color-light);
  border-radius: 16px;
  border: 1px solid var(--el-border-color-light);
  font-size: 13px;
  color: var(--el-text-color-secondary);
  cursor: default;
  transition: all .15s;
  max-width: 200px;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}
.upload-item:hover {
  background: var(--el-fill-color);
}
.upload-icon {
  flex-shrink: 0;
  opacity: .5;
}
.upload-close {
  flex-shrink: 0;
  cursor: pointer;
  opacity: .4;
  transition: opacity .15s;
}
.upload-close:hover { opacity: 1; color: var(--el-color-danger); }
.upload-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 5rem;
}

.input-textarea {
  flex: 1;
  border: none;
  outline: none;
  resize: none;
  font-size: 15px;
  line-height: 1.6;
  max-height: 160px;
  min-height: 36px;
  background: transparent;
  color: var(--el-text-color-primary);
  font-family: inherit;
  padding: 6px 0;
  margin: 4px 0;
}
.input-textarea::placeholder { color: var(--el-text-color-placeholder); }
.input-textarea:disabled { opacity: .6; }

.input-btns {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 4px;
  min-height: 38px;
}
.input-btns-left,
.input-btns-right {
  display: flex;
  align-items: center;
  gap: 4px;
}
.input-btn {
  border: none;
  background: none;
  cursor: pointer;
  padding: 8px;
  border-radius: 10px;
  color: var(--el-text-color-secondary);
  transition: all .15s;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
}
.input-btn:hover { background: var(--el-fill-color-light); color: var(--el-text-color-primary); }

.send-btn {
  border: none;
  cursor: pointer;
  padding: 8px;
  border-radius: 12px;
  width: 38px;
  height: 38px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  transition: all .15s;
}
.send-btn:hover { opacity: .9; transform: scale(1.05); }
.send-btn:disabled { opacity: .4; cursor: not-allowed; transform: none; }

.stop-btn { background: var(--el-color-danger-light-9); color: var(--el-color-danger); }
.stop-btn:hover { background: var(--el-color-danger-light-7); color: var(--el-color-danger); }

.file-input-hidden { display: none; }

/* ─── Responsive ─── */
@media (max-width: 768px) {
  .chat-sidebar {
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    z-index: 100;
    transform: translateX(-100%);
    transition: transform .25s;
    box-shadow: 4px 0 20px rgba(0,0,0,0.1);
  }
  .chat-sidebar.open { transform: translateX(0); }
  .menu-btn { display: inline-flex; }
  .header-model-select { display: none; }
  .sidebar-footer .model-select-wrapper { display: flex; }
  .msg-body { max-width: 90%; }
  .welcome { padding: 60px 16px 32px; }
  .welcome-title { font-size: 22px; }
  .welcome-suggestions { gap: 8px; }
  .suggestion-chip { font-size: 12px; padding: 8px 14px; }
  .input-area { left: 0; }
  .input-box-container { padding: 0 10px 12px; }
  .input-box { min-height: 90px; border-radius: 18px; padding: 10px 14px 6px; }
  .input-textarea { font-size: 14px; }
  .messages-area { padding: 0 0 160px; }
}
@media (min-width: 769px) {
  .sidebar-footer .model-select-wrapper { display: flex; }
}
</style>

<style>
/* ─── Global Markdown Styles ─── */
.chat-page .msg-text.markdown-body pre {
  position: relative;
  background: #1e1e2e;
  border-radius: 10px;
  padding: 16px;
  overflow-x: auto;
  margin: 10px 0;
  border: 1px solid rgba(255,255,255,0.06);
}
.chat-page .msg-text.markdown-body pre code {
  font-size: 13px;
  line-height: 1.6;
  color: #cdd6f4;
}
.chat-page .msg-text.markdown-body .copy-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  padding: 4px 10px;
  font-size: 11px;
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 6px;
  background: rgba(255,255,255,0.06);
  color: #a6adc8;
  cursor: pointer;
  opacity: 0;
  transition: opacity .2s;
}
.chat-page .msg-text.markdown-body pre:hover .copy-btn { opacity: 1; }
.chat-page .msg-text.markdown-body .copy-btn:hover { background: rgba(255,255,255,0.12); color: #cdd6f4; }
.chat-page .msg-text.markdown-body p { margin: 6px 0; }
.chat-page .msg-text.markdown-body ul, .chat-page .msg-text.markdown-body ol { padding-left: 20px; }
.chat-page .msg-text.markdown-body a { color: var(--el-color-primary); text-decoration: underline; }
.chat-page .msg-text.markdown-body blockquote {
  border-left: 3px solid var(--el-color-primary);
  padding-left: 14px;
  color: var(--el-text-color-secondary);
  margin: 10px 0;
}
.chat-page .msg-text.markdown-body table {
  border-collapse: collapse;
  width: 100%;
  margin: 10px 0;
  font-size: 13px;
}
.chat-page .msg-text.markdown-body th,
.chat-page .msg-text.markdown-body td {
  border: 1px solid var(--el-border-color);
  padding: 8px 12px;
  text-align: left;
}
.chat-page .msg-text.markdown-body th {
  background: var(--el-fill-color-light);
  font-weight: 600;
}
.chat-page .msg-text.markdown-body details {
  margin: 8px 0;
}
.chat-page .msg-text.markdown-body details summary {
  cursor: pointer;
  color: var(--el-color-primary);
  font-size: 13px;
  font-weight: 600;
}
</style>
