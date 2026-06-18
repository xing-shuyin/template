<template>
    <template v-for="(item, index) in data" :key="index">
        <el-sub-menu v-if="item?.children?.length" :index="item.path" popper-class="menu-poper">
            <template #title>
                <!-- 有子集的菜单icon要放到title里 -->
                <Icon :icon="item.icon" v-if="item.icon" class="menu-icon" />
                <span class="menu-text">{{ item.label }}</span>
            </template>
            <menutree :data="item.children" :parent_path="parent_path + '/' + item.path"></menutree>
        </el-sub-menu>
        <el-menu-item v-else :route="parent_path + '/' + item.path" :index="parent_path + '/' + item.path"
            @click="add_menus_tab(item)">
            <!-- 没有子集的菜单icon要放到title外 -->
            <Icon :icon="item.icon" v-if="item.icon" class="menu-icon" />
            <template #title>
                <span class="menu-text">{{ item.label }}</span>
            </template>
        </el-menu-item>
    </template>
</template>
<script setup>
import store from '@/utils/store';
import { Icon } from '@iconify/vue';  //https://www.npmjs.com/package/@iconify/vue
import { duplicate_object } from '@/utils/tool'
const props = defineProps(['data', 'parent_path'])

const add_menus_tab = (item) => {
    if (item.name != "index") { //TAG:固定的标签
        store().menus_tab.push({ label: item.label, name: item.name });
        store().menus_tab = duplicate_object(store().menus_tab, "name");
    }
    store().current_menu = item.name;
};

</script>
<style lang="scss">
.menu-poper {
    background-color: var(--menu-tree-poper-bg);
}

.menu-text {
    user-select: none;
    font-size: 13px;
    text-decoration: none !important;
    margin-left: 5px;
}

.el-menu--collapse {
    .menu-icon {
        margin: auto;
    }

    .menu-text {
        display: none !important;
    }
}
</style>
