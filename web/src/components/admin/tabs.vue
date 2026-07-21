<script setup>
import store from '@/utils/store'
import { onBeforeMount } from 'vue';
const router = useRouter()
const route = useRoute()
const default_page = { label: '首页', name: 'index' }  //默认菜单路由name
const menus_tab_change = (tab) => {
    router.push({ name: tab.props.name })
}
const menus_tab_remove = (tab) => {
    if (tab != store().current_menu) {
        store().menus_tab = store().menus_tab.filter((i) => {
            return i.name != tab
        })
    } else {
        store().menus_tab = store().menus_tab.filter((i, index) => {
            if (i.name != tab) return true;
            else {
                if (index != 0) {
                    store().current_menu = store().menus_tab[index - 1].name
                    router.push({ name: store().menus_tab[index - 1].name })
                    return false
                } else {
                    store().current_menu = default_page.name
                    router.push({ name: default_page.name })
                }

            }
        })
    }
}
const menus_tab_close_all = () => {
    store().menus_tab = []
    store().current_menu = default_page.name
    router.push({ name: default_page.name })
}
const menus_tab_close_other = () => {
    store().menus_tab = store().menus_tab.filter((i) => {
        return i.name == store().current_menu
    })
}
const menus_tab_close_left = () => {
    let finded = false;
    store().menus_tab = store().menus_tab.filter((i) => {
        if (i.name == store().current_menu) {
            finded = true
        }
        if (!finded) return false;
        else return true
    })
}
const menus_tab_close_right = () => {
    let finded = false;
    store().menus_tab = store().menus_tab.filter((i) => {
        if (i.name == store().current_menu) {
            finded = true
            return true
        } else {
            if (!finded) return true;
            else return false
        }
    })
}
watch(() => { return store().menus_tab }, () => {
    localStorage.setItem('menus_tab', JSON.stringify(store().menus_tab))
})
onBeforeMount(() => {
    if (localStorage.getItem('menus_tab')) {
        store().menus_tab = JSON.parse(localStorage.getItem('menus_tab'))
    }
    store().current_menu = route.name
})
</script>
<template>
    <div class="menu-tab">
        <!-- TAG:菜单标签 -->
        <el-tabs v-model="store().current_menu" type="card" @tab-remove="menus_tab_remove"
            @tab-click="menus_tab_change">
            <el-tab-pane key="aritcle" :label="default_page.label" :name="default_page.name" :closable="false">
            </el-tab-pane>
            <el-tab-pane v-for="item in store().menus_tab" :key="item.name" :label="item.label" :name="item.name"
                closable>
            </el-tab-pane>
        </el-tabs>
        <div class="menu-tab-tool">
            <el-dropdown split-button @click="menus_tab_close_all">
                <mdi:close-circle></mdi:close-circle>
                <template #dropdown>
                    <el-dropdown-menu>
                        <el-dropdown-item @click="menus_tab_close_all">关闭全部</el-dropdown-item>
                        <el-dropdown-item @click="menus_tab_close_other">关闭其他</el-dropdown-item>
                        <el-dropdown-item @click="menus_tab_close_left">关闭左侧</el-dropdown-item>
                        <el-dropdown-item @click="menus_tab_close_right">关闭右侧</el-dropdown-item>
                    </el-dropdown-menu>
                </template>
            </el-dropdown>
        </div>
    </div>
</template>
<style scoped lang='scss'>
.menu-tab {
    position: relative;
    border-bottom-left-radius: 10px;
    border-bottom-right-radius: 10px;
    overflow: hidden;
    margin-right: 10px;

    ::deep(.el-tabs) {
        .el-tabs__header {
            margin-bottom: 0;
        }

        .el-tabs__item {
            box-sizing: border-box;
            color: var(--admin-tab-item-color);
            user-select: none;
        }

        .el-tabs__item.is-active,
        .el-tabs__item:hover {
            color: var(--admin-tab-item-hover-color);
        }

        background-color: var(--admin-tab-bg);


        .is-active {
            // 激活tab颜色
            background-color: var(--admin-tab-avtive-bg);
        }
    }


    .menu-tab-tool {
        position: absolute;
        right: 0;
        top: 50%;
        transform: translateY(-50%);

        ::deep(.el-dropdown) {
            .el-button:hover {
                color: var(--admin-tab-tool-hover-color);
            }
        }
    }
}
</style>
