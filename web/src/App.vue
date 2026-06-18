<script setup>
import { useDark } from '@vueuse/core'
import bus from '@/utils/bus';
const router = useRouter()
const isDark = useDark()
bus.on('logout', () => {
    localStorage.removeItem('access_token')
    router.push('/login')
})
bus.on('response:error', (error) => {
    // 响应错误处理
    if (error.response && error.response.status === 401) {
        console.log('401');
        // token过期处理
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        // 跳转到登录页面
        // 清空cookie
        if (error.response.data.detail) {
            ElMessage({
                message: error.response.data.detail,
                grouping: true,
            })
        } else {
            ElMessage({
                message: '账号或密码错误',
                grouping: true,
            })
        }

        router.push('/login')
    } else if (error.response && error.response.status === 403) {
        console.log('403');
        // 没有权限
        // 跳转到无权限页面
        router.push('/403')
    }
})
// document.addEventListener('contextmenu', (e) => {
//     e.preventDefault(); // 阻止默认右键菜单
// });
</script>
<template>
    <!-- <Suspense>

    </Suspense> -->
    <div>
        <router-view></router-view>
    </div>
</template>
<style scoped></style>
