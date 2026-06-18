import store from '@/utils/store'

export function hasPerm(code) {
  const buttons = store().permissions?.buttons || []
  return buttons.includes(code)
}

export default {
  install(app) {
    app.config.globalProperties.$hasPerm = hasPerm
    app.directive('perm', {
      mounted(el, binding) {
        if (binding.value && !hasPerm(binding.value)) {
          el.parentNode?.removeChild(el)
        }
      },
      updated(el, binding) {
        if (binding.value && !hasPerm(binding.value)) {
          el.parentNode?.removeChild(el)
        }
      },
    })
  },
}
