import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../views/HomePage.vue'
import GeneratorPage from '../views/GeneratorPage.vue'
import SocialMediaPage from '../views/SocialMediaPage.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePage
  },
  {
    path: '/generator',
    name: 'Generator',
    component: GeneratorPage
  },
  {
    path: '/social-media',
    name: 'SocialMedia',
    component: SocialMediaPage
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router