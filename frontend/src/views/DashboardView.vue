<template>
  <div class="container">
    <h1>Welcome, {{ username }}!</h1>
    <p>This is your protected dashboard.</p>
    <div v-if="message" class="flash">{{ message }}</div>
    <div v-if="!is_2fa_enabled">
      <button @click="goToEnable2FA">Enable 2FA</button>
    </div>
    <div v-else>
      <p>2FA is enabled.</p>
    </div>
    <button @click="logout">Logout</button>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      username: '',
      is_2fa_enabled: false,
      message: ''
    }
  },
  async mounted() {
    try {
      const res = await axios.get('http://localhost:8000/dashboard', {
        withCredentials: true
      })
      this.username = res.data.username
      this.is_2fa_enabled = res.data.is_2fa_enabled
      this.message = res.data.message
      if (res.data.redirect) {
        localStorage.removeItem('session_id')
        this.$router.push(res.data.redirect)
      }
    } catch (err) {
      this.message = err.response?.data?.message || 'Error loading dashboard'
      if (err.response?.data?.redirect) {
        localStorage.removeItem('session_id')
        this.$router.push(err.response.data.redirect)
      }
    }
  },
  methods: {
    goToEnable2FA() {
      this.$router.push('/enable_2fa')
    },
    async logout() {
      try {
        const res = await axios.get('http://localhost:8000/logout', {
          withCredentials: true
        })
        localStorage.removeItem('session_id')
        localStorage.removeItem('username')
        this.message = res.data.message
        if (res.data.redirect) {
          this.$router.push(res.data.redirect)
        }
      } catch (err) {
        this.message = err.response?.data?.message || 'Error logging out'
        if (err.response?.data?.redirect) {
          this.$router.push(err.response.data.redirect)
        }
      }
    }
  }
}
</script>

<style scoped>
.container { max-width: 400px; margin: 0 auto; padding: 20px; }
.flash { color: red; margin-bottom: 10px; }
button { padding: 10px 20px; margin: 5px; }
</style>