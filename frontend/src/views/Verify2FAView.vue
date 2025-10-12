<template>
  <div class="container">
    <h1>Enter 2FA Code</h1>
    <div v-if="message" class="flash">{{ message }}</div>
    <form @submit.prevent="verify">
      <label for="otp">6-Digit Code:</label>
      <input type="text" id="otp" v-model="otp" required /><br /><br />
      <input type="submit" value="Verify" />
    </form>
    <a @click="$router.push('/login')">Back to Login</a>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      otp: "",
      message: "",
    };
  },
  methods: {
    async verify() {
      try {
        const res = await axios.post(
          "http://localhost:8000/verify_2fa",
          new URLSearchParams({
            otp: this.otp,
          }),
          {
            withCredentials: true,
          }
        );
        localStorage.setItem("session_id", "active");
        this.message = res.data.message;
        if (res.data.redirect) {
          this.$router.push(res.data.redirect);
        }
      } catch (err) {
        this.message = err.response?.data?.message || "Error verifying 2FA";
        if (err.response?.data?.redirect) {
          localStorage.removeItem("session_id");
          this.$router.push(err.response.data.redirect);
        }
      }
    },
  },
};
</script>

<style scoped>
.container {
  max-width: 400px;
  margin: 0 auto;
  padding: 20px;
}
.flash {
  color: red;
  margin-bottom: 10px;
}
input {
  width: 100%;
  padding: 8px;
  margin: 5px 0;
}
a {
  cursor: pointer;
  color: blue;
  text-decoration: underline;
}
</style>
