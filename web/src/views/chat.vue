<template>
  <div class="chat-wrap">
    <!-- Sidebar -->
    <transition name="sidebar-slide">
      <aside v-if="!sidebarCollapsed" class="chat-sidebar">
        <div class="sidebar-inner">
          <div class="sidebar-top">
            <button class="new-chat-btn" @click="newChat()">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
              新对话
            </button>
          </div>
          <div class="sidebar-list">
            <div v-for="c in filteredChats" :key="c.id" class="sidebar-item"
              :class="{ active: currentChat?.id === c.id }"
              @click="switchChat(c)">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
              <span class="sidebar-item-name">{{ c.name || '新对话' }}</span>
              <button class="sidebar-item-del" @click.stop="deleteChat(c.id)">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
              </button>
            </div>
            <div v-if="!chats.length" class="sidebar-empty">暂无对话</div>
          </div>
        </div>
      </aside>
    </transition>

    <!-- Main -->
    <div class="chat-main">
      <!-- Header bar (always visible) -->
      <header class="chat-header">
        <button class="header-btn md-hidden" @click="sidebarOpen = !sidebarOpen">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 5h16"/><path d="M4 12h16"/><path d="M4 19h16"/></svg>
        </button>
        <button class="header-btn hidden-md" @click="sidebarCollapsed = !sidebarCollapsed">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M9 3v18"/></svg>
        </button>
        <span class="header-title">{{ currentChat?.name || 'New Chat' }}</span>
        <div class="header-actions">
          <button class="header-btn" disabled>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v13"/><path d="m16 6-4-4-4 4"/><path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"/></svg>
          </button>
        </div>
      </header>

      <!-- Messages -->
      <div class="messages-area" ref="messagesRef">
        <div v-if="!messages.length" class="welcome">
          <h1 class="welcome-title">How can I help you today?</h1>
          <div class="welcome-suggestions">
            <button v-for="s in suggestions" :key="s" class="suggestion-chip" @click="quickSend(s)">
              {{ s }}
            </button>
          </div>
        </div>

        <div v-else class="thread">
          <div v-for="(msg, i) in messages" :key="i" class="msg-row" :class="msg.role">
            <div class="msg-row-inner">
              <div class="msg-content">
                <button v-if="msg.role === 'user'" class="edit-btn" @click="branchFrom(i)" title="编辑">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/></svg>
                </button>
                <div v-if="msg.role === 'user'" class="msg-text">{{ msg.content }}</div>
                <div v-else class="msg-text markdown-body" v-html="renderMarkdown(msg.content)" />
              </div>
            </div>
            <div class="msg-actions">
              <button v-if="msg.role === 'assistant'" class="msg-action-btn" @click="copyMessage(msg.content)" title="复制">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
              </button>
              <button v-if="msg.role === 'assistant'" class="msg-action-btn" @click="regenerate(i)" title="重新生成" :disabled="isLoading">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>
              </button>
            </div>
          </div>

          <div v-if="isLoading" class="msg-row assistant">
            <div class="msg-row-inner">
              <div class="msg-content">
                <div class="thinking-dots"><span /><span /><span /></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Input -->
      <div class="input-area">
        <div class="input-box">
          <textarea
            v-model="input"
            class="input-textarea"
            placeholder="Send a message... (@ to mention, / for commands)"
            :disabled="isLoading"
            @keydown.enter.exact="sendMessage()"
            @input="autoResize"
            ref="textareaRef"
            rows="1"
          />
          <!-- 输入框底部工具栏 -->
          <div class="input-toolbar">
            <div class="input-toolbar-left">
              <button class="toolbar-btn">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 4v16m8-8H4"/></svg>
              </button>
              <button class="model-select-btn" @click="sidebarCollapsed = false">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                {{ currentModelName }}
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9l6 6 6-6"/></svg>
              </button>
            </div>
            <div class="input-toolbar-right">
              <button class="toolbar-btn tooltip-btn">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"/></svg>
              </button>
              <button v-if="isLoading" class="stop-btn" @click="stop()">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="6" width="12" height="12" rx="1"/></svg>
                停止生成
              </button>
              <button v-else class="send-btn" :disabled="!input.trim()" @click="sendMessage()">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
              </button>
            </div>
          </div>
        </div>
        <p class="input-footer">AI 可能会产生不准确的信息，请注意甄别。</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
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
      return `<pre class="hljs"><button class="copy-code" onclick="navigator.clipboard.writeText(this.nextElementSibling.textContent)">复制</button><code>${code}</code></pre>`
    } catch {
      return `<pre class="hljs"><code>${escapeHtml(str)}</code></pre>`
    }
  }
})
const escapeHtml = s => s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
const renderMarkdown = (content) => content ? md.render(content) : ''

/* ─── useChatSSE composable ─── */
function useChatSSE({ onError } = {}) {
  const messages = ref([])
  const input = ref('')
  const isLoading = ref(false)
  const currentChat = ref(null)
  const chats = ref([])
  let abortController = null

  async function loadChats() {
    try {
      const res = await r.get('/chat/', { params: { limit: 100, sort: '-created_at' } })
      chats.value = (res.data?.data || []).map(c => ({ ...c, model_name: c.model || '' }))
    } catch (_) {}
  }
  async function loadMessages(chatId) {
    try {
      const res = await r.get(`/chat/${chatId}`)
      currentChat.value = { ...res.data, model_name: res.data.model || '' }
      messages.value = res.data.messages || []
      nextTick(scrollToBottom)
    } catch (_) { ElMessage.error('加载对话失败') }
  }
  function switchChat(chat) {
    if (isLoading.value || chat?.id === currentChat.value?.id) return
    currentChat.value = chat; loadMessages(chat.id)
  }
  function newChat() { currentChat.value = null; messages.value = []; input.value = '' }
  async function deleteChat(chatId) {
    if (isLoading.value) return
    try {
      await r.delete(`/chat/${chatId}/`)
      chats.value = chats.value.filter(c => c.id !== chatId)
      if (currentChat.value?.id === chatId) newChat()
      ElMessage.success('已删除')
    } catch (_) { ElMessage.error('删除失败') }
  }
  let _currentModelId = null
  function setModel(id) { _currentModelId = id }
  function getModelId() { return _currentModelId }
  async function _ensureChat() {
    if (currentChat.value?.id) return currentChat.value.id
    const res = await r.post('/chat/', { name: '', model: '', messages: [], role_id: null })
    const c = res.data; currentChat.value = { ...c, model_name: '' }; chats.value.unshift({ ...c, model_name: '' })
    return c.id
  }
  async function _doSend(chatId) {
    if (isLoading.value) return; isLoading.value = true
    scrollToBottom()
    const aiIdx = messages.value.length; messages.value.push({ role: 'assistant', content: '' })
    let full = ''; abortController = new AbortController()
    try {
      const token = localStorage.getItem('access_token')
      const res = await fetch('/api/chat/proxy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) },
        body: JSON.stringify({ messages: messages.value.filter(m => m.content).map(m => ({ role: m.role, content: m.content })), model_id: getModelId(), chat_id: chatId }),
        signal: abortController.signal, credentials: 'include',
      })
      if (!res.ok) throw new Error((await res.json().catch(() => ({}))).detail || '请求失败')
      const reader = res.body.getReader(); const decoder = new TextDecoder(); let buf = ''
      while (true) {
        const { done, value } = await reader.read(); if (done) break
        buf += decoder.decode(value, { stream: true })
        for (const line of buf.split('\n')) {
          const t = line.trim()
          if (!t.startsWith('data: ')) continue; const s = t.slice(6)
          if (s === '[DONE]') continue
          try { const d = JSON.parse(s); if (d.choices?.[0]?.delta?.content) { full += d.choices[0].delta.content; messages.value[aiIdx] = { role: 'assistant', content: full }; scrollToBottom() } } catch {}
        }
        buf = ''
      }
    } catch (err) {
      messages.value[aiIdx] = { role: 'assistant', content: err.name === 'AbortError' ? full + '\n\n*（已停止）*' : `*错误：${err.message}*` }
      if (err.name !== 'AbortError') onError?.(err)
    } finally { isLoading.value = false; abortController = null; scrollToBottom(); loadChats() }
  }
  async function sendMessage() {
    const text = input.value.trim(); if (!text || isLoading.value) return
    if (!getModelId()) { ElMessage.warning('请先选择模型'); return }
    let chatId; try { chatId = await _ensureChat() } catch { ElMessage.error('创建对话失败'); return }
    messages.value.push({ role: 'user', content: text }); input.value = ''; _doSend(chatId)
  }
  function stop() { abortController?.abort() }
  function regenerate(idx) {
    if (isLoading.value) return
    let u = idx - 1; while (u >= 0 && messages.value[u].role !== 'user') u--
    if (u < 0) return; messages.value = messages.value.slice(0, u + 1); _doSend(currentChat.value?.id)
  }
  function branchFrom(idx) {
    if (isLoading.value) return; const m = messages.value[idx]
    messages.value = messages.value.slice(0, m?.role === 'user' ? idx : idx + 1)
    if (m?.role === 'user') input.value = m.content || ''
  }
  return { messages, input, isLoading, currentChat, chats, loadChats, switchChat, newChat, deleteChat, setModel, sendMessage, stop, regenerate, branchFrom }
}

const sidebarCollapsed = ref(false); const sidebarOpen = ref(false); const searchText = ref(''); const messagesRef = ref(null); const models = ref([]); const currentModelId = ref(null); const textareaRef = ref(null)
const chat = useChatSSE({ onError: err => ElMessage.error(err.message) })
const { messages, input, isLoading, currentChat, chats } = chat
const { switchChat, deleteChat, newChat, loadChats, setModel, sendMessage, stop, regenerate, branchFrom } = chat

const currentModelName = computed(() => {
  const m = models.value.find(m => m.id === currentModelId.value)
  return m?.label || m?.name || '选择模型'
})
const suggestions = ['Weather', 'Code', 'Write', 'History']
const filteredChats = computed(() => {
  if (!searchText.value) return chats.value
  const q = searchText.value.toLowerCase()
  return chats.value.filter(c => (c.name || '').toLowerCase().includes(q))
})
function quickSend(text) { input.value = text; sendMessage() }
function copyMessage(content) { navigator.clipboard.writeText(content || '').then(() => ElMessage.success('已复制')) }
function scrollToBottom() { nextTick(() => { const e = messagesRef.value; if (e) e.scrollTop = e.scrollHeight }) }
function autoResize() { const e = textareaRef.value; if (!e) return; e.style.height = 'auto'; e.style.height = Math.min(e.scrollHeight, 200) + 'px' }
watch(() => messages.value?.length, () => scrollToBottom())

onMounted(async () => {
  try { const res = await r.get('/chat/models/'); models.value = res.data?.data || []; if (models.value.length) { currentModelId.value = models.value[0].id; chat.setModel(models.value[0].id) } } catch {}
  await loadChats()
})
</script>

<style scoped>

.chat-wrap {
  display: flex; height: 100vh; overflow: hidden;
  background: var(--chat-bg); color: var(--chat-fg);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

/* ─── Custom scrollbar ─── */
.messages-area::-webkit-scrollbar,
.sidebar-list::-webkit-scrollbar {
  width: 8px;
}
.messages-area::-webkit-scrollbar-track,
.sidebar-list::-webkit-scrollbar-track {
  background: transparent;
}
.messages-area::-webkit-scrollbar-thumb,
.sidebar-list::-webkit-scrollbar-thumb {
  background: #333;
  border-radius: 4px;
}
.messages-area::-webkit-scrollbar-thumb:hover,
.sidebar-list::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* ─── Sidebar ─── */
.chat-sidebar {
  width: 260px; min-width: 260px;
  background: var(--chat-sidebar-bg);
  display: flex; flex-direction: column;
  border-right: 1px solid var(--chat-sidebar-border);
  transition: all .2s;
}
.sidebar-inner { display: flex; flex-direction: column; height: 100%; }
.sidebar-top { padding: 16px 12px 12px; }
.new-chat-btn {
  display: flex; align-items: center; gap: 8px;
  width: 100%; padding: 8px 12px;
  border: none; border-radius: 10px;
  background: var(--chat-sidebar-accent); color: var(--chat-sidebar-fg);
  font-size: 13px; font-weight: 500; cursor: pointer; transition: background .15s;
}
.new-chat-btn:hover { background: #333; }
.new-chat-btn svg { width: 16px; height: 16px; }
.sidebar-list { flex: 1; overflow-y: auto; padding: 0 8px 8px; }
.sidebar-item {
  display: flex; align-items: center; gap: 10px;
  padding: 6px 10px; border-radius: 10px; cursor: pointer;
  font-size: 13px; transition: background .15s; position: relative;
  color: var(--chat-sidebar-muted);
  margin-bottom: 2px;
}
.sidebar-item:hover { background: var(--chat-sidebar-accent); color: var(--chat-sidebar-fg); }
.sidebar-item[data-active], .sidebar-item.active { background: var(--chat-sidebar-accent); color: #fff; }
.sidebar-item-name { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.sidebar-item-del {
  opacity: 0; border: none; background: none; cursor: pointer;
  color: var(--chat-sidebar-muted); padding: 4px; border-radius: 4px; transition: opacity .15s;
}
.sidebar-item:hover .sidebar-item-del { opacity: 1; }
.sidebar-item-del:hover { color: #ef4444; background: rgba(255,255,255,.1); }
.sidebar-empty { text-align: center; color: var(--chat-sidebar-muted); padding: 32px; font-size: 13px; }
.sidebar-slide-enter-active, .sidebar-slide-leave-active { transition: all .2s; }
.sidebar-slide-enter-from, .sidebar-slide-leave-to { width: 0; min-width: 0; opacity: 0; overflow: hidden; }

/* ─── Main ─── */
.chat-main { flex: 1; display: flex; flex-direction: column; min-width: 0; background: #000; }

/* ─── Header bar ─── */
.chat-header {
  display: flex; align-items: center; gap: 8px;
  height: 56px; padding: 0 16px; flex-shrink: 0;
  border-bottom: 1px solid rgba(39, 39, 42, 0.5);
}
.header-title {
  font-size: 14px; font-weight: 500; color: #d4d4d4;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  min-width: 0;
}
.header-actions { margin-left: auto; display: flex; align-items: center; gap: 4px; }
.header-btn {
  border: none; background: none; cursor: pointer;
  color: var(--chat-muted-fg); padding: 6px; border-radius: var(--chat-radius);
  display: flex; align-items: center; transition: background .15s;
}
.header-btn:hover { background: var(--chat-accent); color: var(--chat-accent-fg); }
@media (max-width: 768px) { .hidden-md { display: none !important; } }
@media (min-width: 769px) { .md-hidden { display: none !important; } }

/* ─── Messages ─── */
.messages-area { flex: 1; overflow-y: auto; padding: 16px 0; }

/* Welcome */
.welcome {
  display: flex; flex-direction: column; align-items: center;
  justify-content: center; height: 100%; padding: 40px 32px 80px;
}
.welcome-title { font-size: 24px; font-weight: 600; color: #fff; margin-bottom: 32px; }
.welcome-suggestions {
  display: flex; flex-wrap: wrap; gap: 8px; justify-content: center;
  max-width: 500px; width: 100%;
}
.suggestion-chip {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 6px 16px; border: 1px solid var(--chat-sidebar-border);
  border-radius: 9999px; background: #1a1a1a;
  font-size: 12px; cursor: pointer; text-align: left;
  color: var(--chat-muted-fg); transition: all .15s;
  white-space: nowrap;
}
.suggestion-chip:hover { border-color: #52525b; color: var(--chat-accent-fg); }
.suggestion-chip:active { transform: scale(.97); }

/* Thread */
.thread { max-width: var(--chat-thread-max-width); margin: 0 auto; padding: 8px 0 32px; }
.msg-row { padding: 0 16px; }
.msg-row-inner {
  display: flex; gap: 16px; padding: 12px 0;
  max-width: var(--chat-thread-max-width); margin: 0 auto;
  position: relative;
}
/* User message row - right aligned */
.msg-row.user .msg-row-inner {
  justify-content: flex-end;
}
.msg-content { flex: 1; min-width: 0; }
.msg-text {
  font-size: 15px; line-height: 1.85;
  white-space: normal; word-break: break-word;
  color: var(--chat-fg);
}
/* User message bubble */
.msg-row.user .msg-text {
  background: lab(15.204% 0 -.00000596046);
  border-radius: 16px;
  border-bottom-right-radius: 4px;
  padding: 8px 16px;
  display: inline-block;
  max-width: 80%;
  color: var(--chat-accent-fg);
  white-space: pre-wrap;
}
.msg-row.user .msg-content {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 4px;
}
.msg-row.user .msg-content .edit-btn {
  flex-shrink: 0;
}
.msg-text :deep(pre) {
  background: #1e1e1e; color: #d4d4d4;
  padding: 12px 14px; border-radius: var(--chat-radius);
  overflow-x: auto; margin: 6px 0; position: relative;
}
.msg-text :deep(code) { font-family: 'Fira Code', 'Cascadia Code', monospace; font-size: 13px; }
.msg-text :deep(p) { margin: 0; padding: 0; line-height: 1.85; }
.msg-text :deep(ul), .msg-text :deep(ol) {
  padding-left: 1.5em;
  margin: 0;
}
.msg-text :deep(li) {
  margin: 0;
  padding-left: 0;
}
.msg-text :deep(li::marker) {
  color: var(--chat-muted-fg);
}
.msg-text :deep(table) { border-collapse: collapse; width: 100%; margin: 4px 0; }
.msg-text :deep(th), .msg-text :deep(td) { border: 1px solid var(--chat-border); padding: 4px 8px; }
.msg-text :deep(th) { background: var(--chat-muted); font-weight: 600; }
.msg-text :deep(strong) { color: #fff; }
.msg-text :deep(h1), .msg-text :deep(h2), .msg-text :deep(h3), .msg-text :deep(h4) { margin: 6px 0 1px; color: #fff; }
.msg-text :deep(blockquote) { border-left: 3px solid var(--chat-border); margin: 4px 0; padding: 2px 12px; color: var(--chat-muted-fg); }
.msg-text :deep(hr) { margin: 6px 0; }

/* Message actions */
.msg-actions {
  display: flex; gap: 2px; align-items: center;
  padding: 2px 0 0;
  margin-left: 0;
}
.msg-action-btn {
  width: 24px; height: 24px; border: none; border-radius: var(--chat-radius);
  background: transparent; color: #71717a;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: all .15s;
}
.msg-action-btn:hover { color: var(--chat-accent-fg); }
.msg-action-btn:disabled { opacity: .3; cursor: not-allowed; }
.msg-action-btn:active { transform: scale(.9); }

/* Edit button on user messages */
.edit-btn {
  border: none; background: none; cursor: pointer;
  color: #71717a; padding: 4px; border-radius: 4px;
  display: flex; align-items: center; justify-content: center;
  opacity: 0; transition: all .15s;
}
.edit-btn svg { width: 16px; height: 16px; }
.msg-row.user:hover .edit-btn { opacity: 1; }
.edit-btn:hover { color: var(--chat-accent-fg); }

/* Thinking */
.thinking-dots { display: flex; gap: 4px; padding: 8px 0; align-items: center; }
.thinking-dots span {
  width: 8px; height: 8px; border-radius: 50%;
  background: var(--chat-muted-fg);
  animation: dotPulse 1.4s infinite ease-in-out;
}
.thinking-dots span:nth-child(2) { animation-delay: .2s; }
.thinking-dots span:nth-child(3) { animation-delay: .4s; }
@keyframes dotPulse { 0%,60%,100% { opacity: .3; } 30% { opacity: 1; } }

/* ─── Composer ─── */
.input-area {
  padding: 16px 16px 24px;
  background: #000;
}
.input-box {
  max-width: var(--chat-thread-max-width);
  margin: 0 auto;
  background: color-mix(in oklab, lab(15.204% 0 -.00000596046) 30%, lab(2.75381% 0 0));
  border-radius: 1.5rem;
  border: 1px solid rgba(63, 63, 70, 0.5);
  box-shadow: 0 10px 15px -3px rgba(0,0,0,0.3);
  transition: border-color .2s;
}
.input-box:focus-within {
  border-color: #52525b;
}
.input-textarea {
  width: 100%; border: none; background: transparent;
  resize: none; font-size: 15px; line-height: 1.5;
  color: #fff; outline: none;
  font-family: inherit; max-height: 200px; box-sizing: border-box;
  padding: 11px 16px;
  
  min-height: 45px;
}
.input-textarea::placeholder { color: #71717a; }
/* Input toolbar */
.input-toolbar {
  display: flex; justify-content: space-between; align-items: center;
  padding: 0 12px 12px;
}
.input-toolbar-left, .input-toolbar-right {
  display: flex; align-items: center; gap: 4px;
}
.toolbar-btn {
  border: none; background: none; cursor: pointer;
  color: #a1a1aa; padding: 6px; border-radius: 6px;
  display: flex; align-items: center; transition: all .15s;
}
.toolbar-btn:hover { background: rgba(255,255,255,.08); color: #e4e4e7; }
.tooltip-btn {
  padding: 8px;
}
.model-select-btn {
  display: flex; align-items: center; gap: 6px;
  border: 1px solid rgba(63, 63, 70, 0.5);
  background: rgba(39, 39, 42, 0.5);
  color: #a1a1aa;
  padding: 6px 10px; border-radius: 9999px;
  font-size: 12px; cursor: pointer; transition: all .15s;
}
.model-select-btn:hover { background: rgba(63, 63, 70, 0.5); color: #fff; }
.send-btn, .stop-btn {
  border: none; border-radius: 50%; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all .15s;
}
.send-btn {
  width: 36px; height: 36px;
  background: #52525b; color: #fff;
}
.send-btn:disabled { opacity: .4; cursor: not-allowed; }
.send-btn:not(:disabled):hover { background: #71717a; }
.send-btn:not(:disabled):active { transform: scale(.9); }
.stop-btn {
  gap: 6px; padding: 6px 14px; border-radius: 9999px;
  background: var(--chat-muted); color: var(--chat-fg);
  font-size: 13px;
}
.stop-btn:hover { background: var(--chat-border); }
.input-footer {
  text-align: center; font-size: 12px; color: var(--chat-muted-fg);
  max-width: var(--chat-thread-max-width); margin: 8px auto 0;
}
</style>

<style>
/* ─── Dark theme ─── */
:root {
  --chat-bg: #000000;
  --chat-fg: #d4d4d4;
  --chat-muted: #262626;
  --chat-muted-fg: #a1a1aa;
  --chat-border: #27272a;
  --chat-border-light: rgba(63, 63, 70, 0.5);
  --chat-accent: #262626;
  --chat-accent-fg: #e4e4e7;
  --chat-primary: #fafafa;
  --chat-primary-fg: #0a0a0a;
  --chat-radius: 0.5rem;
  --chat-thread-max-width: 700px;
  --chat-composer-radius: 1.5rem;
  --chat-composer-padding: 8px;
  --chat-sidebar-bg: #171717;
  --chat-sidebar-fg: #e4e4e7;
  --chat-sidebar-muted: #a1a1aa;
  --chat-sidebar-border: #27272a;
  --chat-sidebar-accent: #262626;
  --color-muted: #262626;
  --color-background: #000000;
}
.copy-code {
  position: absolute; top: 8px; right: 8px;
  padding: 4px 10px; font-size: 12px;
  border: none; border-radius: 4px;
  background: rgba(255,255,255,.1); color: #a3a3a3;
  cursor: pointer; transition: background .2s;
}
.copy-code:hover { background: rgba(255,255,255,.2); color: #fff; }
</style>
