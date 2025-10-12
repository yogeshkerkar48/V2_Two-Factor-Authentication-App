<template>
  <div class="container">
    <h1>Enable Two-Factor Authentication</h1>
    <div v-if="message" class="flash">{{ message }}</div>
    <p>Scan this QR code using your authenticator app (e.g., Google Authenticator):</p>
    <img v-if="qr_code" :src="'data:image/png;base64,' + qr_code" alt="2FA QR Code">
    <p>Or enter this secret manually: <strong>{{ secret }}</strong></p>
    <form @submit.prevent="enable2FA">
      <input type="hidden" v-model="secret">
      <button type="submit">Enable 2FA</button>
    </form>
    <a @click="$router.push('/dashboard')">Cancel</a>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      qr_code: '',
      secret: '',
      message: ''
    }
  },
  async mounted() {
    try {
      const res = await axios.get('http://localhost:8000/enable_2fa', {
        withCredentials: true
      })
      this.qr_code = res.data.qr_code
      this.secret = res.data.secret
      this.message = res.data.message
      if (res.data.redirect) {
        localStorage.removeItem('session_id')
        this.$router.push(res.data.redirect)
      }
    } catch (err) {
      this.message = err.response?.data?.message || 'Error loading 2FA setup'
      if (err.response?.data?.redirect) {
        localStorage.removeItem('session_id')
        this.$router.push(err.response.data.redirect)
      }
    }
  },
  methods: {
    async enable2FA() {
      try {
        const res = await axios.post('http://localhost:8000/enable_2fa', new URLSearchParams({
          secret: this.secret
        }), {
          withCredentials: true
        })
        this.message = res.data.message
        if (res.data.redirect) {
          this.$router.push(res.data.redirect)
        }
      } catch (err) {
        this.message = err.response?.data?.message || 'Error enabling 2FA'
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
img { max-width: 200px; margin: 10px 0; }
button { padding: 10px 20px; margin: 5px; }
a { cursor: pointer; color: blue; text-decoration: underline; }
</style>