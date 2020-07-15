<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="4">
        <v-card class="elevation-12">
          <v-toolbar color="primary" dark flat>
            <v-toolbar-title>Login form</v-toolbar-title>
            <v-spacer></v-spacer>
            <v-btn v-on:click="changeLoginval">{{ Loginval }}</v-btn>
          </v-toolbar>

          <div id="login" v-if="this.login">
            <v-card-text>
              <v-form>
                <v-text-field
                  label="Email"
                  name="login"
                  prepend-icon="mdi-account"
                  type="text"
                  v-model="input.username_login"
                ></v-text-field>
                <v-text-field
                  id="password"
                  label="Password"
                  name="password"
                  prepend-icon="mdi-lock"
                  type="password"
                  v-model="input.password_login"
                ></v-text-field>
              </v-form>
            </v-card-text>
          </div>
          <div id="register" v-if="this.login === false">
            <v-card-text>
              <v-form>
                <v-text-field
                  label="Register with Email"
                  name="login"
                  prepend-icon="mdi-account"
                  type="text"
                  v-model="input.username"
                ></v-text-field>

                <v-text-field
                  id="password"
                  label="Password"
                  name="password"
                  prepend-icon="mdi-lock"
                  type="password"
                  v-model="input.password"
                ></v-text-field>
              </v-form>
            </v-card-text>
          </div>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn
              color="primary"
              v-if="this.login === false"
              v-on:click.prevent="register()"
              >Register me!</v-btn
            >
            <v-btn
              color="primary"
              v-if="this.login"
              v-on:click.prevent="loggin_in()"
              >Log me in!</v-btn
            >
          </v-card-actions>
          <div id="inactive" v-if="this.show_inactive">
            <p>
              You account is not active yet! Send Email to
              {{ this.input.username }}?
            </p>
            <v-btn
              color="primary"
              v-if="this.login"
              v-on:click.prevent="confirm()"
              >Send Email</v-btn
            >
          </div>
          <div id="wrong_credentials" v-if="this.wrong_credentials">
            <p>Wrong credentials!</p>
          </div>
          <div id="success" v-if="this.success">
            <p>Login successful!</p>
          </div>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import axios from "axios";
export default {
  props: {
    source: String
  },
  data: () => ({
    input: {
      username: "",
      password: "",
      username_login: "",
      password_login: ""
    },
    success: false,
    show_inactive: false,
    login: false,
    Loginval: "Register",
    wrong_credentials: false
  }),
  methods: {
    changeLoginval() {
      if (this.login) {
        this.login = false;
        this.Loginval = "Register";
      } else {
        this.login = true;
        this.Loginval = "Login";
      }
    },
    register() {
      if (this.input.username != "" && this.input.password != "") {
        axios
          .post("http://localhost:5000/register", {
            email: this.input.username,
            password: this.input.password
          })
          .then(function(data) {
            console.log(data);
          })
          .catch(function(e) {
            console.log(e);
          });
      }
    },
    loggin_in() {
      if (this.input.username_login != "" && this.input.password_login != "") {
        axios
          .post("http://localhost:5000/login", {
            email: this.input.username_login,
            password: this.input.password_login
          })
          .then(data => {
            if (data.status === 200) {
              this.success = true;
              this.wrong_credentials = false;
              this.show_inactive = false;
            }
          })
          .catch(error => {
            this.success = false;
            if (error.response.data["message"] === "User not activated") {
              console.log(error.response.data["message"]);
              this.show_inactive = true;
              this.wrong_credentials = false;
            } else {
              this.wrong_credentials = true;
              this.show_inactive = false;
            }
          });
      }
    },
    confirm() {
      if (this.input.username_login != "") {
        console.log(this.input.username_login);
        axios
          .post("http://localhost:5000/confirm", {
            email: this.input.username
          })
          .then(data => {
            console.log(data);
          })
          .catch(error => {
            console.log(error);
          });
      }
    }
  }
};
</script>

<style scoped>
.v-btn {
  width: 150px;
}
#inactive,
#wrong_credentials {
  padding: 10px 10px;
  background: red;
  color: white;
  border: 1px solid lightgray;
  display: block;
  margin-top: 15px;
}

#success {
  padding: 10px 10px;
  background: green;
  color: white;
  border: 1px solid lightgray;
  display: block;
  margin-top: 15px;
}
</style>
