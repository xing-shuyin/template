import store from '@/utils/store'

/**
 * 检查当前用户是否拥有指定的权限码（按钮级/元素级权限）
 * @param {string} code - 权限标识（如 "system:user:add"）
 * @returns {boolean} 是否拥有该权限
 */
export function hasPerm(code) {
  // 从 store 中获取当前用户的按钮级权限码列表
  // 用于控制页面上具体操作元素（按钮、链接、Tab 等）的显示隐藏
  const buttons = store().permissions?.buttons || []
  // 判断权限码是否在列表中
  return buttons.includes(code)
}

export default {
  /**
   * Vue 插件安装方法
   * 注册全局方法 $hasPerm 和自定义指令 v-perm
   */
  install(app) {
    // 全局挂载 $hasPerm 方法，可在模板中通过 this.$hasPerm(code) 调用
    app.config.globalProperties.$hasPerm = hasPerm

    // 注册 v-perm 指令：根据权限码控制元素显示/隐藏
    app.directive('perm', {
      // 元素挂载时检查权限，无权限则移除该元素
      mounted(el, binding) {
        if (binding.value && !hasPerm(binding.value)) {
          el.parentNode?.removeChild(el)
        }
      },
      // 元素更新时重新检查权限（适用于权限动态变化的场景）
      updated(el, binding) {
        if (binding.value && !hasPerm(binding.value)) {
          el.parentNode?.removeChild(el)
        }
      },
    })
  },
}

/* ============================================================
 *  使用示例（Usage Examples）
 * ============================================================
 *
 *  【配置流程】
 *  1. 后端 Button 表添加按钮权限记录，如 code="user:add"
 *  2. 在角色管理中将该按钮授权给角色
 *  3. 用户登录后自动加载权限到 store.permissions.buttons
 *
 *  【方式一】v-perm 指令（推荐）
 *  <el-button v-perm="'user:add'" @click="addUser">添加用户</el-button>
 *  <el-button v-perm="'user:edit'" type="primary" link @click="edit(row)">编辑</el-button>
 *  <el-popconfirm v-perm="'user:delete'" title="确定删除吗?" @confirm="del(row)">
 *    <template #reference>
 *      <el-button type="danger" link>删除</el-button>
 *    </template>
 *  </el-popconfirm>
 *
 *  【方式二】$hasPerm() 方法（用于 v-if 等灵活场景）
 *  <el-button v-if="$hasPerm('user:export')" @click="exportData">导出</el-button>
 *  <el-tab-pane v-if="$hasPerm('tab:secret')" label="机密" name="secret">...</el-tab-pane>
 *
 *  【方式三】JS 中使用
 *  import { hasPerm } from '@/utils/perm'
 *  if (hasPerm('user:add')) { ... }
 * ============================================================ */
