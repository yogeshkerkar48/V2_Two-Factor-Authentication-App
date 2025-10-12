import { createRouter, createWebHistory } from "vue-router";
import RegisterView from "../views/RegisterView.vue";
import LoginView from "../views/LoginView.vue";
import DashboardView from "../views/DashboardView.vue";
import Enable2FAView from "../views/Enable2FAView.vue";
import Verify2FAView from "../views/Verify2FAView.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: "/", name: "register", component: RegisterView },
    { path: "/login", name: "login", component: LoginView },
    {
      path: "/dashboard",
      name: "dashboard",
      component: DashboardView,
      meta: { requiresAuth: true },
    },
    {
      path: "/enable_2fa",
      name: "enable_2fa",
      component: Enable2FAView,
      meta: { requiresAuth: true },
    },
    { path: "/verify_2fa", name: "verify_2fa", component: Verify2FAView },
  ],
});

router.beforeEach((to, from, next) => {
  const sessionId = localStorage.getItem("session_id");
  if (to.meta.requiresAuth && !sessionId) {
    next("/login");
  } else {
    next();
  }
});

export default router;
