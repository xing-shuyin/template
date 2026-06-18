import { createRouter, createWebHistory } from 'vue-router'
import store from './store';
import r from './request'

const views = { ...import.meta.glob("@/views/admin/*/*.vue"), ...import.meta.glob("@/views/admin/*.vue") };

const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: '/chat/',
            name: 'chat',
            component: () => import('../views/chat.vue'),
            meta: { title: "AI 对话" },
        },
        {
            path: '/:catchAll(.*)',
            name: '404',
            component: () => import('../views/404.vue'),
            hidden: true,
            meta: { title: "" }
        },
        {
            path: '/login/',
            name: 'login',
            component: () => import('../views/login.vue'),
        },
        {
            path: '/admin/',
            name: 'layout',
            component: () => import('../views/admin/system/layout.vue'),
            meta: { title: "后台管理" },
            children: []
        },
        {
            path: '/admin/profile/',
            name: 'profile',
            component: () => import('../views/admin/system/profile.vue'),
            meta: { title: "用户信息" },
            children: []
        },
    ],

})
console.log(router);

const initrouter = (to, next) => {
    store().loadMe(false).then((data) => {
        const menus_tree = data.menus_tree || []
        // 给每个菜单挂上 component 引用
        const flatten = (list) => {
            list.forEach(m => {
                if (!m.is_catalog && m.component) {
                    m.component = views[`/src/views/${m.component}`]
                }
                if (m.children) flatten(m.children)
            })
        }
        flatten(menus_tree)
        store().menus = menus_tree
        store().menus.forEach((m) => {
            m.meta = { title: m.label }
            router.addRoute('layout', m)
        })
        if (next) {
            next(to.path)
        }
    })
};
router.beforeEach((to, from, next) => {
    if (to.meta.title) {
        document.title = to.meta.title // 修改页面标题
    }
    if (to.path.startsWith("/admin")) {
        if (store().menus.length == 0) {
            initrouter(to, next)
        } else {

            next()
        }
    } else {
        next()
    }
})

export default router