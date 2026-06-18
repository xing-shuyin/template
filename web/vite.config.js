import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import Icons from 'unplugin-icons/vite'
import IconsResolver from 'unplugin-icons/resolver'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'
import path from 'path'

export default defineConfig({
  base: '/',
  server: {
    host: '0.0.0.0',
    port: 3000,
    open: 'http://127.0.0.1:3000',
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8091',
        ws: true,
        changeOrigin: true,
      },
      '/public': {
        target: 'http://127.0.0.1:8091',
        changeOrigin: true,
      }
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    }
  },
  plugins: [
    vue(),
    Components({
      extensions: ['vue'],
      resolvers: [
        ElementPlusResolver({
          importStyle: 'css',
          directives: true,
          exclude: /^(ElColorPicker|ElDatePicker)/
        }),
        IconsResolver({
          prefix: false
        }),
      ],
      include: [/\.vue$/, /\.vue\?vue/],
    }),
    Icons({ /* options */ }),
    AutoImport({
      imports: [
        'vue',
        'vue-router'
      ],
      resolvers: [ElementPlusResolver()],
    }),
  ],
})