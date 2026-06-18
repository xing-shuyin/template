import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from '@/utils/router'
import '@/style.scss'
import App from './App.vue'
const pinia = createPinia()
import ElementPlus from 'element-plus'
import 'element-plus/theme-chalk/dark/css-vars.css'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import 'highlight.js/styles/github-dark.css'
import permPlugin from '@/utils/perm'
createApp(App).
    use(pinia).
    use(ElementPlus, {
        locale: zhCn,
    }).
    use(router).
    use(permPlugin).
    mount('#app')