import Vue from 'vue'
import VueRouter from 'vue-router'
import { MdButton,
         MdApp,
         MdIcon,
         MdToolbar,
         MdContent,
         MdDrawer,
         MdList,
         MdTable,
       } from 'vue-material/dist/components'
import 'vue-material/dist/vue-material.min.css'
import 'vue-material/dist/theme/default-dark.css'

import App from './App.vue'
import ThingList from './components/ThingList.vue'
import Thing from './components/Thing.vue'

Vue.config.productionTip = false

Vue.use(VueRouter)

Vue.use(MdButton)
Vue.use(MdApp)
Vue.use(MdIcon)
Vue.use(MdToolbar)
Vue.use(MdContent)
Vue.use(MdDrawer)
Vue.use(MdList)
Vue.use(MdTable)

const routes = [
  { path: '/', component: ThingList },
  { path: '/things/:id', component: Thing },
]

const router = new VueRouter({
  routes
})

new Vue({
  router,
  render: h => h(App),
}).$mount('#app')
