<template>
    <div class="layout">
        <!-- 侧边栏 -->
        <div class="side" :class="{ 'collapsed': store().toggle_side }">
            <div class="logo">
                <img src="/logo.png" alt="Logo">
                <!-- <transition name="fade">. -->
                <span v-if="!store().toggle_side" class="logo-text">后台管理系统</span>
                <!-- </transition> -->
            </div>

            <el-scrollbar class="menu-scrollbar">
                <el-menu class="menu" router :collapse="store().toggle_side" :default-active="route.fullPath"
                    unique-opened :background-color="isDark ? '#1a1a1a' : '#ffffff'"
                    :text-color="isDark ? '#a1a1aa' : '#4a5568'" :active-text-color="isDark ? '#ffffff' : '#1a202c'">
                    <menutree :data="store().menus" parent_path="/admin" />
                </el-menu>
            </el-scrollbar>

            <div class="side-footer">
                <div class="toggle-btn" @click="store().toggle_side = !store().toggle_side">
                    <Icon :icon="store().toggle_side ? 'ep:expand' : 'ep:fold'" />
                </div>
            </div>
        </div>

        <!-- 主内容区 -->
        <div class="main-container">
            <!-- 顶部导航 -->
            <div class="header">
                <div class="header-left">
                    <el-breadcrumb separator="/">
                        <el-breadcrumb-item v-for="(item, index) in breadcrumbs" :key="index">
                            {{ item }}
                        </el-breadcrumb-item>
                    </el-breadcrumb>
                </div>

                <div class="header-right">
                    <div class="action-item" @click="goChat">
                        <Icon icon="fluent:chat-32-regular" />
                    </div>
                    <div class="action-item" @click="toggleFullscreen">
                        <Icon
                            :icon="isFullscreen ? 'proicons:full-screen-minimize' : 'proicons:full-screen-maximize'" />
                    </div>
                    <theme class="action-item" />

                    <el-dropdown trigger="click">
                        <div class="user-profile">
                            <el-avatar :src="userinfo.avatar" :size="30" />
                        </div>
                        <template #dropdown>
                            <el-dropdown-menu>
                                <el-dropdown-item @click="router.push('/admin/profile/')">
                                    <Icon icon="ep:user" /> {{ userinfo.fullname }}
                                </el-dropdown-item>
                                <el-dropdown-item divided @click="store().logout">
                                    <Icon icon="ep:switch-button" /> 退出登录
                                </el-dropdown-item>
                            </el-dropdown-menu>
                        </template>
                    </el-dropdown>
                </div>
            </div>

            <!-- 标签页 (可选) -->
            <!-- <tabs /> -->

            <!-- 主内容 -->
            <div class="content">
                <router-view v-slot="{ Component }">
                    <!-- <transition name="fade-transform" mode="out-in"> -->
                    <component :is="Component" />
                    <!-- </transition> -->
                </router-view>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useFullscreen } from '@vueuse/core'
import { Icon } from '@iconify/vue'
import store from '@/utils/store'
import { useDark } from '@vueuse/core'

const router = useRouter()
const route = useRoute()
const { isFullscreen, toggle: toggleFullscreen } = useFullscreen()
const isDark = useDark()

const userinfo = computed(() => store().user || {})
store().loadMe()
const goChat = () => {
  window.location.href = '/chat/'
}
// 计算面包屑导航
const breadcrumbs = computed(() => {
    return route.matched
        .filter(item => item.meta && item.meta.title)
        .map(item => item.meta.title)
})
</script>

<style lang="scss">
:root {
    /* 基础变量 */
    --header-height: 60px;
    --side-width: 240px;
    --side-collapsed-width: 64px;
    --side-logo-height: 60px;
    --transition-time: 0.3s;

    /* 浅色主题 */
    --bg-color: #f5f7fa;
    --text-color: #333;
    --text-color-light: #666;
    --border-color: #e4e7ed;
    --primary-color: #409eff;
    --success-color: #67c23a;
    --warning-color: #e6a23c;
    --danger-color: #f56c6c;
    --info-color: #909399;

    /* 侧边栏 */
    --side-bg: #ffffff;
    --side-text-color: #4a5568;
    --side-active-bg: #f0f4f8;
    --side-active-text: #1a202c;
    --side-hover-bg: #f5f7fa;

    /* 顶部导航 */
    --header-bg: #ffffff;
    --header-text: #333;
    --header-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);

    /* 内容区 */
    --content-bg: #ffffff;
    --content-radius: 8px;
    --content-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);



    --header-bg: #ffffff;
    --input-bg: #f8fafc;
    --border-color: #e2e8f0;
    --primary-color: #3b82f6;
    --primary-color-rgb: 59, 130, 246;
}

.dark {
    /* 深色主题 */
    --bg-color: #0f0f0f;
    --text-color: #e5e5e5;
    --text-color-light: #a1a1aa;
    --border-color: #2d2d2d;
    --primary-color: #3a7bd5;

    /* 侧边栏 */
    --side-bg: #1a1a1a;
    --side-text-color: #a1a1aa;
    --side-active-bg: #2d2d2d;
    --side-active-text: #ffffff;
    --side-hover-bg: #252525;

    /* 顶部导航 */
    --header-bg: #1a1a1a;
    --header-text: #e5e5e5;
    --header-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);

    /* 内容区 */
    --content-bg: #1e1e1e;

    --input-bg: #1e293b;
    --border-color: #334155;

}



.main {
    flex: 1;
    // height: 100%;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    background-color: var(--admin-main-bg);
    border-radius: 12px;
    box-shadow: var(--admin-main-box-shadow);
    padding: 5px;
    transition: all 0.3s ease;

    /* 顶部操作区域 */
    .main-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 16px;

        background: var(--header-bg);
        // border-radius: 8px;
        // border-top-left-radius: 8px;
        // border-top-right-radius: 8px;
        box-shadow: 6px 0 8px -6px rgba(0, 0, 0, 0.1),
            -6px 0 8px -6px rgba(0, 0, 0, 0.1);
        // margin-bottom: 16px;
        position: relative;

        .search {
            display: flex;
            align-items: center;
            gap: 12px;
            flex-grow: 1;
            max-width: 600px;

            .el-input {
                flex: 1;
                min-width: 200px;

                :deep(.el-input__wrapper) {
                    border-radius: 6px;
                    background: var(--input-bg);
                    box-shadow: 0 0 0 1px var(--border-color);
                    transition: all 0.3s ease;

                    &:hover {
                        box-shadow: 0 0 0 1px var(--primary-color);
                    }

                    &.is-focus {
                        box-shadow: 0 0 0 1px var(--primary-color),
                            0 2px 8px rgba(var(--primary-color-rgb), 0.2);
                    }
                }
            }
        }

        .tool {
            display: flex;
            align-items: center;
            gap: 8px;

            .el-button {
                padding: 8px 16px;
                border-radius: 6px;
                transition: all 0.3s ease;

                &.is-circle {
                    width: 36px;
                    height: 36px;
                    padding: 8px;

                    .btn-icon {
                        font-size: 16px;
                    }
                }

                &:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                }

                &:active {
                    transform: translateY(0);
                }
            }
        }

        &::after {
            content: "";
            position: absolute;
            left: 0;
            right: 0;
            bottom: -8px;
            height: 1px;
            background: linear-gradient(90deg, transparent, var(--border-color), transparent);
        }
    }

    /* 表格区域 */
    .main-table {
        padding: 5px;
        box-sizing: border-box;
        flex: 1;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        background-color: var(--content-bg);
        // border-radius: 8px;
        box-shadow: var(--content-shadow);

        .el-table {
            flex: 1;
            --el-table-border-color: var(--border-color);
            --el-table-header-bg-color: var(--content-bg);
            --el-table-tr-bg-color: var(--content-bg);
            --el-table-row-hover-bg-color: var(--admin-main-table-row-hover-bg);
            --el-table-current-row-bg-color: var(--admin-main-table-current-row-bg);

            :deep(.el-table__header) {
                th {
                    background-color: var(--content-bg);
                    color: var(--text-color);
                    font-weight: 600;
                    height: 48px;
                }
            }

            :deep(.el-table__body) {
                tr {
                    td {
                        transition: background-color 0.2s ease;
                    }

                    &:hover td {
                        background-color: var(--admin-main-table-row-hover-bg) !important;
                    }
                }
            }

            /* 操作列按钮样式 */
            :deep(.el-button--text) {
                padding: 6px 8px;
                font-size: 13px;
                transition: all 0.2s ease;

                &.el-button--primary {
                    color: var(--primary-color);

                    &:hover {
                        background-color: rgba(var(--primary-color-rgb), 0.1);
                    }
                }

                &.el-button--danger {
                    color: var(--danger-color);

                    &:hover {
                        background-color: rgba(var(--danger-color-rgb), 0.1);
                    }
                }
            }
        }
    }

    /* 底部页码 */
    .main-foot {
        display: flex;
        justify-content: flex-end;
        // margin-top: 16px;

        .el-pagination {

            :deep(.btn-prev),
            :deep(.btn-next),
            :deep(.number) {
                width: 36px;
                height: 36px;
                border-radius: 8px;
                margin: 0 4px;
                transition: all 0.2s ease;

                &:hover {
                    color: var(--primary-color);
                    background-color: rgba(var(--primary-color-rgb), 0.1);
                }
            }

            :deep(.is-active) {
                background-color: var(--primary-color);
                color: white;
            }
        }
    }

    /* 对话框样式 */
    .admin_detail_dialog {
        :deep(.el-dialog) {
            border-radius: 12px;
            overflow: hidden;
            background-color: var(--content-bg);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);

            .el-dialog__header {
                display: none;
            }

            .el-dialog__body {
                padding: 24px;

                .el-form {
                    .el-form-item {
                        margin-bottom: 20px;

                        .el-form-item__label {
                            color: var(--text-color);
                            font-weight: 500;
                        }

                        .el-input,
                        .el-cascader {
                            :deep(.el-input__wrapper) {
                                border-radius: 8px;
                                background-color: var(--content-bg);
                                box-shadow: 0 0 0 1px var(--border-color);

                                &:hover {
                                    box-shadow: 0 0 0 1px var(--primary-color);
                                }
                            }
                        }
                    }
                }
            }

            .el-dialog__footer {
                padding: 16px 24px;
                border-top: 1px solid var(--border-color);
                text-align: right;

                .el-button {
                    padding: 10px 20px;
                    border-radius: 8px;
                    transition: all 0.2s ease;

                    &--primary {
                        background-color: var(--primary-color);
                        border-color: var(--primary-color);

                        &:hover {
                            opacity: 0.9;
                            transform: translateY(-1px);
                        }
                    }
                }
            }
        }
    }
}

/* 暗黑模式适配 */
.dark {
    .main {
        .main-top {
            .search {
                .el-input {
                    :deep(.el-input__inner) {
                        color: var(--text-color);
                    }
                }
            }
        }

        .el-table {
            --el-table-text-color: var(--text-color);
            --el-table-header-text-color: var(--text-color);
        }

        .admin_detail_dialog {
            :deep(.el-dialog) {
                .el-form {
                    .el-form-item__label {
                        color: var(--text-color);
                    }
                }
            }
        }
    }
}
</style>

<style scoped lang="scss">
.layout {
    position: relative;
    width: 100vw;
    height: 100vh;
    overflow: hidden;
    display: flex;
    background-color: var(--bg-color);
    color: var(--text-color);
    transition: background-color var(--transition-time);
}

/* 侧边栏样式 */
.side {
    width: var(--side-width);
    height: 100%;
    background-color: var(--side-bg);
    display: flex;
    flex-direction: column;
    transition: width var(--transition-time);
    box-shadow: 2px 0 8px rgba(0, 0, 0, 0.05);
    z-index: 10;

    &.collapsed {
        width: var(--side-collapsed-width);

        .logo-text {
            opacity: 0;
            width: 0;
        }
    }

    .logo {
        height: var(--side-logo-height);
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0 16px;
        border-bottom: 1px solid var(--border-color);
        transition: padding var(--transition-time);

        img {
            width: 32px;
            height: 32px;
            transition: all var(--transition-time);
        }

        .logo-text {
            margin-left: 12px;
            font-size: 18px;
            font-weight: 600;
            white-space: nowrap;
            transition: all var(--transition-time);
            color: var(--text-color);
        }
    }

    .menu-scrollbar {
        flex: 1;
        overflow: hidden;

        :deep(.el-scrollbar__view) {
            height: 100%;
        }

        .menu {
            height: 100%;
            border-right: none;

            :deep(.el-menu-item),
            :deep(.el-sub-menu__title) {
                height: 48px;
                line-height: 48px;
                transition: all var(--transition-time);

                &:hover {
                    background-color: var(--side-hover-bg);
                }

                &.is-active {
                    background-color: var(--side-active-bg);
                    font-weight: 500;
                }
            }
        }
    }

    .side-footer {
        padding: 12px;
        border-top: 1px solid var(--border-color);

        .toggle-btn {
            width: 100%;
            height: 36px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            border-radius: 4px;
            transition: all var(--transition-time);

            &:hover {
                background-color: var(--side-hover-bg);
            }

            .iconify {
                font-size: 20px;
                color: var(--text-color-light);
            }
        }
    }
}

/* 主内容区 */
.main-container {

    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;

    .header {
        height: var(--header-height);
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 20px;
        background-color: var(--header-bg);
        box-shadow: var(--header-shadow);
        z-index: 9;
        user-select: none;

        .header-left {
            .el-breadcrumb {
                font-size: 14px;

                :deep(.el-breadcrumb__inner) {
                    color: var(--text-color-light);
                    transition: color var(--transition-time);

                    &.is-link {
                        font-weight: normal;
                    }
                }
            }
        }

        .header-right {
            display: flex;
            align-items: center;
            gap: 10px;

            .action-item {
                display: flex;
                align-items: center;
                justify-content: center;
                width: 36px;
                height: 36px;
                cursor: pointer;
                border-radius: 50%;
                transition: all var(--transition-time);

                &:hover {
                    background-color: var(--side-hover-bg);
                }

                .iconify {
                    font-size: 18px;
                    color: var(--text-color-light);
                }

                &:hover {
                    transform: scale(1.1);
                    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
                }
            }

            .user-profile {
                display: flex;
                align-items: center;
                cursor: pointer;
                padding: 4px 8px;
                border-radius: 18px;
                transition: all var(--transition-time);

                &:hover {
                    background-color: var(--side-hover-bg);
                }

                .username {
                    margin: 0 8px;
                    font-size: 14px;
                }

                .iconify {
                    font-size: 14px;
                    color: var(--text-color-light);
                }
            }
        }
    }

    .content {
        flex: 1;
        // padding: 16px;
        display: flex;
        flex-direction: column;
        overflow: hidden;
        background-color: var(--bg-color);

        // >div {
        //     height: 100%;
        //     background-color: var(--content-bg);
        //     border-radius: var(--content-radius);
        //     box-shadow: var(--content-shadow);
        //     overflow: hidden;
        // }
    }
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
    transition: opacity var(--transition-time);
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
}

.fade-transform-enter-active,
.fade-transform-leave-active {
    transition: all var(--transition-time);
}

.fade-transform-enter-from {
    opacity: 0;
    transform: translateY(20px);
}

.fade-transform-leave-to {
    opacity: 0;
    transform: translateY(-20px);
}
</style>