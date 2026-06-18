<template>
    <div class="profile-page">
        <div class="profile-header">
            <div class="avatar-wrapper">
                <div class="avatar" :style="{ backgroundImage: `url(${user.avatar || 'data:image/svg+xml,...'})` }">
                    <span v-if="!user.avatar">{{ (user.fullname || 'U')[0] }}</span>
                </div>
                <div class="avatar-info">
                    <h2>{{ user.fullname || '未设置姓名' }}</h2>
                    <p class="avatar-email">{{ user.email }}</p>
                    <el-tag v-if="user.is_superuser" type="danger" size="small">超级管理员</el-tag>
                    <el-tag v-else type="info" size="small">普通用户</el-tag>
                </div>
            </div>
        </div>

        <div class="profile-body">
            <el-tabs v-model="activeTab">
                <el-tab-pane label="基本信息" name="info">
                    <el-form :model="profileForm" label-width="100px" class="profile-form">
                        <el-form-item label="用户名">
                            <el-input v-model="profileForm.fullname" placeholder="请输入姓名" />
                        </el-form-item>
                        <el-form-item label="邮箱">
                            <el-input v-model="profileForm.email" disabled />
                        </el-form-item>
                        <el-form-item label="头像链接">
                            <el-input v-model="profileForm.avatar" placeholder="头像 URL" />
                        </el-form-item>
                        <el-form-item label="注册时间">
                            <el-input :model-value="user.created_at" disabled />
                        </el-form-item>
                        <el-form-item>
                            <el-button type="primary" @click="updateProfile" :loading="saving">保存修改</el-button>
                        </el-form-item>
                    </el-form>
                </el-tab-pane>

                <el-tab-pane label="修改密码" name="password">
                    <el-form :model="pwdForm" label-width="100px" class="profile-form" :rules="pwdRules" ref="pwdFormRef">
                        <el-form-item label="当前密码" prop="old_password">
                            <el-input v-model="pwdForm.old_password" type="password" show-password />
                        </el-form-item>
                        <el-form-item label="新密码" prop="new_password">
                            <el-input v-model="pwdForm.new_password" type="password" show-password />
                        </el-form-item>
                        <el-form-item label="确认密码" prop="new_password_confirm">
                            <el-input v-model="pwdForm.new_password_confirm" type="password" show-password />
                        </el-form-item>
                        <el-form-item>
                            <el-button type="primary" @click="changePwd" :loading="pwdLoading">修改密码</el-button>
                        </el-form-item>
                    </el-form>
                </el-tab-pane>
            </el-tabs>
        </div>
    </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import store from '@/utils/store'
import r from '@/utils/request'

const activeTab = ref('info')
const saving = ref(false)
const pwdLoading = ref(false)
const pwdFormRef = ref(null)

const user = computed(() => store().user || {})

const profileForm = reactive({
    fullname: '',
    email: '',
    avatar: '',
})
const pwdForm = reactive({
    old_password: '',
    new_password: '',
    new_password_confirm: '',
})
const pwdRules = {
    old_password: [{ required: true, message: '请输入当前密码', trigger: 'blur' }],
    new_password: [{ required: true, message: '请输入新密码', trigger: 'blur' }],
    new_password_confirm: [
        { required: true, message: '请确认新密码', trigger: 'blur' },
        { validator: (rule, value, callback) => {
            if (value !== pwdForm.new_password) callback(new Error('两次密码不一致'))
            else callback()
        }, trigger: 'blur' },
    ],
}

onMounted(() => {
    store().loadMe().then(() => {
        profileForm.fullname = user.value.fullname || ''
        profileForm.email = user.value.email || ''
        profileForm.avatar = user.value.avatar || ''
    })
})

const updateProfile = async () => {
    saving.value = true
    try {
        await r.patch(`/user/${user.value.id}/`, {
            fullname: profileForm.fullname,
            avatar: profileForm.avatar,
        })
        ElMessage({ message: '保存成功', type: 'success' })
        store().loadMe(false) // 刷新缓存
    } catch (e) {
        ElMessage({ message: '保存失败', type: 'error' })
    }
    saving.value = false
}

const changePwd = async () => {
    pwdFormRef.value.validate(async (valid) => {
        if (!valid) return
        pwdLoading.value = true
        try {
            await r.post('/login/change_password', {
                old_password: pwdForm.old_password,
                new_password: pwdForm.new_password,
                new_password_confirm: pwdForm.new_password_confirm,
            })
            ElMessage({ message: '密码修改成功', type: 'success' })
            pwdForm.old_password = ''
            pwdForm.new_password = ''
            pwdForm.new_password_confirm = ''
        } catch (e) {
            ElMessage({ message: e.response?.data?.detail || '密码修改失败', type: 'error' })
        }
        pwdLoading.value = false
    })
}
</script>

<style scoped lang="scss">
.profile-page {
    padding: 24px;
    max-width: 720px;
    margin: 0 auto;
}

.profile-header {
    background: var(--content-bg);
    border-radius: 12px;
    padding: 32px;
    margin-bottom: 24px;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);

    .avatar-wrapper {
        display: flex;
        align-items: center;
        gap: 24px;

        .avatar {
            width: 72px;
            height: 72px;
            border-radius: 50%;
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
            font-weight: 700;
            color: #fff;
            background-size: cover;
            background-position: center;
            flex-shrink: 0;
        }

        .avatar-info {
            h2 { margin: 0 0 4px; font-size: 20px; }
            .avatar-email { color: var(--el-text-color-secondary); font-size: 14px; margin: 0 0 8px; }
        }
    }
}

.profile-body {
    background: var(--content-bg);
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.profile-form {
    max-width: 480px;
    margin-top: 16px;
}
</style>
