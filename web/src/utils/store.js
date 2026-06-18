import { defineStore } from "pinia";
import r from "@/utils/request"
import { logout } from '@/utils/tool'
const store = defineStore('store', {
    state: () => ({
        theme: 'dark',
        menus: [],
        menus_tab: [],
        current_menu: 'index',
        toggle_side: false,
        chat_roles: [],
        permissions: { buttons: [], interfaces: [], menus: [] },
    }),
    getters: {
        menu_width: (state) => {
            return state.toggle_side ? '63px' : '200px'
        },
    },
    actions: {
        async loadMe(cache = true) {
            if (cache && this.menus.length > 0) {
                return { user: this.user, permissions: this.permissions, menus_tree: this.menus }
            }
            let res = await r.get("/me/")
            const data = res.data || {}
            this.user = data.user || {}
            this.permissions = data.permissions || { buttons: [], interfaces: [], menus: [] }
            this.menus = data.menus_tree || []
            return data
        },
        logout() {
            logout()
        }
    },
})

export default store;