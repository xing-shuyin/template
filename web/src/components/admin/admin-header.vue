<template>
    <div class="header">
        <div class="left-section">
            <div class="toggle-side" @click="store().toggle_side = !store().toggle_side">
                <Icon v-if="store().toggle_side" icon="ep:expand"></Icon>
                <Icon v-else icon="ep:fold"></Icon>
            </div>
        </div>

        <div class="right-section">
            <theme></theme>
            <el-dropdown>
                <span class="el-dropdown-link">
                    <span>{{ userinfo.fullname }}</span>
                    <img :src="userinfo.avatar" class="user-avatar" alt="用户头像">
                </span>
                <template #dropdown>
                    <el-dropdown-menu>
                        <el-dropdown-item @click="router.push('/admin/profile/')">个人中心</el-dropdown-item>
                        <el-dropdown-item @click="store().logout">退出登录</el-dropdown-item>
                    </el-dropdown-menu>
                </template>
            </el-dropdown>
        </div>
    </div>

</template>
<script setup>
import store from '@/utils/store';
import { Icon } from '@iconify/vue';  //https://www.npmjs.com/package/@iconify/vue

import { useDark, useToggle } from '@vueuse/core'
const isDark = useDark()
const toggleDark = useToggle(isDark)
const userinfo = ref({})
store().userinfo().then((res) => {
    userinfo.value = res
})
</script>
<style scoped lang="scss">
.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: var(--header-height);
    // padding: 10px 20px;
    background-color: var(--admin-header-bg);
    box-shadow: var(--admin-header-box-shadow);
    margin-top: 10px;
    margin-right: 10px;
    border-radius: 10px;

    .left-section {
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: space-between;
        gap: 10px;
    }


    .theme-toggle {
        // position: absolute;
        // top: 30px;
        // right: 30px;
        width: 36px;
        height: 36px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        background: var(--light-gray);
        border-radius: 50%;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;

        &:hover {
            transform: scale(1.1);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }

        svg {
            width: 20px;
            height: 20px;
            color: var(--dark);
        }
    }

    .toggle-side {
        margin-left: 10px;
        cursor: pointer;
        font-size: 20px;
        color: var(--admin-header-toggle-side-color);
    }


    .right-section {
        display: flex;
        align-items: center;
        gap: 15px;
    }

    .el-dropdown-link {
        display: flex;
        align-items: center;
        outline: none;
        cursor: pointer;
        color: var(--admin-header-dropdown-color);
        gap: 5px;
    }

    .user-avatar {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        margin-right: 10px;
    }

    .el-dropdown-menu {
        min-width: 150px;
    }

    .el-dropdown-item {
        font-size: 14px;
    }

    .el-icon--right {
        margin-left: 5px;
    }

    @media (max-width: 768px) {
        .header {
            flex-direction: column;
            align-items: flex-start;
        }

        .left-section {
            margin-bottom: 10px;
        }

        .title {
            margin-bottom: 10px;
        }

        .right-section {
            width: 100%;
            justify-content: flex-end;
        }
    }
}
</style>