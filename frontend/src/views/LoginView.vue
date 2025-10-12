<template>
  <div class="container">
    <h1>Login Page</h1>
    <div v-if="message" class="flash">{{ message }}</div>
    <form @submit.prevent="login">
      <label for="username">Username:</label>
      <input type="text" id="username" v-model="username" required><br><br>
      <label for="password">Password:</label>
      <input type="password" id="password" v-model="password" required><br><br>
      <input type="submit" value="Login">
    </form>
    <p>Don't have an account? <router-link to="/">Register here</router-link>.</p>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      username: '',
      password: '',
      message: ''
    }
  },
  methods: {
    async login() {
      try {
        const res = await axios.post('http://localhost:8000/login', new URLSearchParams({
          username: this.username,
          password: this.password
        }), {
          withCredentials: true
        })
        localStorage.setItem('session_id', 'active') // Simple flag; session managed by backend
        localStorage.setItem('username', this.username) // For verify_2fa
        this.message = res.data.message
        if (res.data.redirect) {
          this.$router.push(res.data.redirect)
        }
      } catch (err) {
        this.message = err.response?.data?.message || 'Error logging in'
      }
    }
  }
}
</script>

<style scoped>
.container { max-width: 400px; margin: 0 auto; padding: 20px; }
.flash { color: red; margin-bottom: 10px; }
input { width: 100%; padding: 8px; margin: 5px 0; }
</style>