<template>
    <div class="login-wrapper">
        <div class="login-container">
            <div class="login-left">
                <div class="branding">
                    <div class="logo">
                        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path
                                d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"
                                fill="currentColor" />
                        </svg>
                    </div>
                    <h1>欢迎来到未来</h1>
                    <p>探索数字世界的无限可能</p>
                </div>
                <div class="particles" id="particles-js"></div>
            </div>

            <div class="login-right">
                <div class="theme-toggle" @click="isDarkMode = !isDarkMode">
                    <svg v-if="isDarkMode" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 3c.132 0 .263 0 .393 0a7.5 7.5 0 0 0 7.92 12.446a9 9 0 1 1-8.313-12.454z"
                            fill="currentColor" />
                    </svg>
                    <svg v-else viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path
                            d="M12 18a6 6 0 1 1 0-12 6 6 0 0 1 0 12zm0-2a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM11 1h2v3h-2V1zm0 19h2v3h-2v-3zM3.515 4.929l1.414-1.414L7.05 5.636 5.636 7.05 3.515 4.93zM16.95 18.364l1.414-1.414 2.121 2.121-1.414 1.414-2.121-2.121zm2.121-14.85l1.414 1.415-2.121 2.121-1.414-1.414 2.121-2.121zM5.636 16.95l1.414 1.414-2.121 2.121-1.414-1.414 2.121-2.121zM23 11v2h-3v-2h3zM4 11v2H1v-2h3z"
                            fill="currentColor" />
                    </svg>
                </div>

                <div class="login-header">
                    <h2>欢迎回来</h2>
                    <p>请登录您的账户</p>
                </div>

                <form ref="form" id="form" method="POST" @keyup.enter="submit" class="login-form">
                    <div class="form-group floating">
                        <input type="email" id="username" name="username" required placeholder=" " />
                        <label for="username">邮箱</label>
                        <div class="underline"></div>
                        <div class="icon">
                            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path
                                    d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"
                                    fill="currentColor" />
                            </svg>
                        </div>
                    </div>

                    <div class="form-group floating">
                        <input type="password" id="password" name="password" required placeholder=" " />
                        <label for="password">密码</label>
                        <div class="underline"></div>
                        <div class="icon">
                            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path
                                    d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71 1.39-3.1 3.1-3.1 1.71 0 3.1 1.39 3.1 3.1v2z"
                                    fill="currentColor" />
                            </svg>
                        </div>
                    </div>

                    <div class="form-group captcha-group floating">
                        <div class="captcha-input">
                            <input type="text" id="captcha" name="captcha" required placeholder=" " />
                            <label for="captcha">验证码</label>
                            <div class="underline"></div>
                            <div class="captcha-image" @click="get_captcha">
                                <img :src="captcha" alt="验证码" />
                                <div class="refresh-icon">
                                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                        <path
                                            d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"
                                            fill="currentColor" />
                                    </svg>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="form-options">
                        <label class="remember-me">
                            <input type="checkbox" name="remember_me" id="remember_me" />
                            <span class="checkmark"></span>
                            记住我
                        </label>
                        <a href="/api/login/reset" class="forgot-password">忘记密码?</a>
                    </div>

                    <div class="error-message" :class="{ show: error }">
                        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path
                                d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"
                                fill="currentColor" />
                        </svg>
                        {{ error }}
                    </div>

                    <button type="button" class="login-button" @click="submit">
                        <span>登录</span>
                        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M10 17l5-5-5-5v10z" fill="currentColor" />
                        </svg>
                    </button>
                </form>

                <div class="social-login">
                    <p>或通过以下方式登录</p>
                    <div class="social-icons">
                        <button class="social-icon google">
                            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path
                                    d="M12.545 10.239v3.821h5.445c-.712 2.315-2.647 3.972-5.445 3.972-3.332 0-6.033-2.701-6.033-6.033s2.701-6.033 6.033-6.033c1.498 0 2.866.549 3.921 1.453l2.814-2.814C17.503 2.332 15.139 1 12.545 1 7.021 1 2.545 5.476 2.545 11s4.476 10 10 10c8.396 0 10-7.496 10-10 0-.671-.069-1.324-.189-1.955H12.545z"
                                    fill="currentColor" />
                            </svg>
                        </button>
                        <button class="social-icon github">
                            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path
                                    d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12z"
                                    fill="currentColor" />
                            </svg>
                        </button>
                        <button class="social-icon twitter">
                            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path
                                    d="M23.954 4.569c-.885.389-1.83.654-2.825.775 1.014-.611 1.794-1.574 2.163-2.723-.951.555-2.005.959-3.127 1.184-.896-.959-2.173-1.559-3.591 1.559-2.717 0-4.92 2.203-4.92 4.917 0 .39.045.765.127 1.124C7.691 8.094 4.066 6.13 1.64 3.161c-.427.722-.666 1.561-.666 2.475 0 1.71.87 3.213 2.188 4.096-.807-.026-1.566-.248-2.228-.616v.061c0 2.385 1.693 4.374 3.946 4.827-.413.111-.849.171-1.296.171-.314 0-.615-.03-.916-.086.631 1.953 2.445 3.377 4.604 3.417-1.68 1.319-3.809 2.105-6.102 2.105-.39 0-.779-.023-1.17-.067 2.189 1.394 4.768 2.209 7.557 2.209 9.054 0 14-7.503 14-14 0-.21-.005-.418-.014-.627.961-.689 1.8-1.56 2.46-2.548l-.047-.02z"
                                    fill="currentColor" />
                            </svg>
                        </button>
                    </div>
                </div>

                <div class="login-footer">
                    还没有账户?
                    <a href="/api/login/register/" class="footer-link">立即注册</a>
                </div>
            </div>
        </div>
    </div>
</template>
<script setup>
import { onMounted, ref } from "vue";
import { useDark, useToggle } from "@vueuse/core";
import r from "@/utils/request";
const router = useRouter();
const form = ref();
const error = ref("");
const captcha = ref("");
const isDarkMode = useDark();
const toggleDark = useToggle(isDarkMode);

// const toggleTheme = () => {
//     isDarkMode.value = !isDarkMode.value
//     localStorage.setItem('darkMode', isDarkMode.value)
// }

const submit = async () => {
    const formdata = new FormData(form.value);
    try {
        const response = await r.post("/login/access/", formdata);
        console.log(response);
        if (response.status === 200) {
            error.value = "登陆成功!";
            router.push("/");
            localStorage.setItem("access_token", response.data.access_token);
            localStorage.setItem("refresh_token", response.data.refresh_token);
        }
    } catch (error) {
        if (error.response) {
            error.value = error.response.data?.detail || "账号或密码不正确";
        } else {
            error.value = "网络错误，请稍后重试";
        }
    }
};

const get_captcha = async () => {
    try {
        const response = await r.get("/captcha/", {
            responseType: "json",
        });

        // Store session_id in localStorage
        localStorage.setItem("session_id_form", response.data.session_id_form);

        // Convert base64 image to blob URL
        const byteCharacters = atob(response.data.image);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {
            byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);
        const blob = new Blob([byteArray], { type: "image/png" });

        // Set the captcha image
        captcha.value = URL.createObjectURL(blob);
    } catch (error) {
        console.error("Failed to get captcha:", error);
    }
};

onMounted(() => {
    get_captcha();

    // 初始化粒子效果
    if (typeof particlesJS !== "undefined") {
        particlesJS("particles-js", {
            particles: {
                number: {
                    value: 80,
                    density: {
                        enable: true,
                        value_area: 800,
                    },
                },
                color: {
                    value: isDarkMode.value ? "#fff" : "#000",
                },
                shape: {
                    type: "circle",
                    stroke: {
                        width: 0,
                        color: "#000000",
                    },
                    polygon: {
                        nb_sides: 5,
                    },
                },
                opacity: {
                    value: 0.5,
                    random: false,
                    anim: {
                        enable: false,
                        speed: 1,
                        opacity_min: 0.1,
                        sync: false,
                    },
                },
                size: {
                    value: 3,
                    random: true,
                    anim: {
                        enable: false,
                        speed: 40,
                        size_min: 0.1,
                        sync: false,
                    },
                },
                line_linked: {
                    enable: true,
                    distance: 150,
                    color: isDarkMode.value ? "#ffffff" : "#000000",
                    opacity: 0.4,
                    width: 1,
                },
                move: {
                    enable: true,
                    speed: 2,
                    direction: "none",
                    random: false,
                    straight: false,
                    out_mode: "out",
                    bounce: false,
                    attract: {
                        enable: false,
                        rotateX: 600,
                        rotateY: 1200,
                    },
                },
            },
            interactivity: {
                detect_on: "canvas",
                events: {
                    onhover: {
                        enable: true,
                        mode: "grab",
                    },
                    onclick: {
                        enable: true,
                        mode: "push",
                    },
                    resize: true,
                },
                modes: {
                    grab: {
                        distance: 140,
                        line_linked: {
                            opacity: 1,
                        },
                    },
                    bubble: {
                        distance: 400,
                        size: 40,
                        duration: 2,
                        opacity: 8,
                        speed: 3,
                    },
                    repulse: {
                        distance: 200,
                        duration: 0.4,
                    },
                    push: {
                        particles_nb: 4,
                    },
                    remove: {
                        particles_nb: 2,
                    },
                },
            },
            retina_detect: true,
        });
    }
});
</script>

<style lang="scss">
@import url("https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap");

.dark {
    .login-wrapper {
        // color: white;
        --primary: #4895ef;
        --primary-light: #4cc9f0;
        --secondary: #4361ee;
        --error: #f72585;
        --success: #4cc9f0;
        --gray: #adb5bd;
        --light-gray: #212529;
        --dark: #f8f9fa;
        --input-border-color: rgba(180, 176, 176, 0.945);
    }
}

.login-wrapper {
    // color: rgb(0, 0, 0);
    --primary: #677ee4;
    --primary-light: #4895ef;
    --secondary: #3f37c9;
    --error: #d88cae;
    --success: #4cc9f0;
    --gray: #6c757d;
    --light-gray: #f8f9fa;
    --dark: #212529;
    --input-border-color: rgba(180, 176, 176, 0.945);
    // 文字禁止选择
    user-select: none;

    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: var(--light-gray);
    font-family: "Poppins", sans-serif;
    position: relative;
    overflow: hidden;
    transition: background-color 0.3s ease;

    &::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg,
                rgba(67, 97, 238, 0.1) 0%,
                rgba(72, 149, 239, 0.1) 100%);
        z-index: 0;
        transition: background 0.3s ease;
    }

    &.dark::before {
        background: linear-gradient(135deg,
                rgba(67, 97, 238, 0.2) 0%,
                rgba(72, 149, 239, 0.2) 100%);
    }
}

.login-container {
    color: var(--dark);
    width: 1000px;
    // height: 600px;
    display: flex;
    background: var(--light-gray);
    border-radius: 20px;
    box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
    overflow: hidden;
    position: relative;
    z-index: 1;
    transition:
        background-color 0.3s ease,
        box-shadow 0.3s ease;

    .dark & {
        box-shadow: 0 15px 30px rgba(0, 0, 0, 0.3);
    }
}

.login-left {
    width: 40%;
    background: linear-gradient(135deg,
            var(--primary) 0%,
            var(--secondary) 100%);

    padding: 50px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    position: relative;
    overflow: hidden;
    transition: background 0.3s ease;

    .branding {
        position: relative;
        z-index: 2;

        .logo {
            width: 60px;
            height: 60px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 30px;
            transition: background 0.3s ease;

            svg {
                width: 30px;
                height: 30px;
            }
        }

        h1 {
            font-size: 28px;
            font-weight: 600;
            margin-bottom: 15px;
            line-height: 1.3;
        }

        p {
            font-size: 16px;
            opacity: 0.9;
            font-weight: 300;
        }
    }

    .particles {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
    }
}

.login-right {
    width: 60%;
    height: fit-content;
    padding: 60px 70px;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    justify-content: center;
    position: relative;

    .theme-toggle {
        position: absolute;
        top: 30px;
        right: 30px;
        width: 36px;
        height: 36px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        background: var(--light-gray);
        border-radius: 50%;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;

        &:hover {
            transform: scale(1.1);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }

        svg {
            width: 20px;
            height: 20px;
            color: var(--dark);
        }
    }

    .login-header {
        margin-bottom: 40px;

        h2 {
            font-size: 26px;
            font-weight: 600;
            color: var(--dark);
            margin-bottom: 8px;
            transition: color 0.3s ease;
        }

        p {
            color: var(--gray);
            font-size: 14px;
            transition: color 0.3s ease;
        }
    }
}

.login-form {
    height: fit-content;

    .form-group {
        position: relative;
        margin-bottom: 25px;
        // overflow: hidden;
        height: fit-content;

        &.floating {
            // overflow: hidden;

            label {
                position: absolute;
                left: 40px;
                top: 18px;
                color: var(--gray);
                font-size: 14px;
                font-weight: 400;
                pointer-events: none;
                transition: all 0.3s ease;
            }

            input {
                box-sizing: border-box;
                width: 100%;
                padding: 18px 40px;
                border: 1px solid var(--input-border-color);
                border-radius: 10px;
                font-size: 14px;
                transition: all 0.3s ease;
                background-color: var(--light-gray);
                color: var(--dark);
                transition: all 0.3s ease;

                &:focus,
                &:not(:placeholder-shown) {
                    background-color: var(--light-gray);
                    border-color: var(--primary-light);
                    box-shadow: 0 5px 15px rgba(67, 97, 238, 0.1);

                    ~label {
                        transform: translateY(-28px) scale(0.85);
                        background: var(--light-gray);
                        padding: 0 5px;
                        left: 35px;
                        color: var(--primary);
                    }

                    ~.icon svg {
                        color: var(--primary);
                    }
                }
            }

            .icon {
                position: absolute;
                left: 15px;
                top: 50%;
                transform: translateY(-50%);

                svg {
                    width: 18px;
                    height: 18px;
                    color: var(--gray);
                    transition: all 0.3s ease;
                }
            }
        }

        &.captcha-group {
            .captcha-input {
                display: flex;
                gap: 15px;

                input {
                    flex: 1;
                }

                .captcha-image {
                    width: 120px;
                    height: 50px;
                    border-radius: 8px;
                    overflow: hidden;
                    position: relative;
                    cursor: pointer;
                    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
                    transition: transform 0.3s ease;

                    &:hover {
                        transform: translateY(-2px);

                        .refresh-icon {
                            opacity: 1;
                        }
                    }

                    img {
                        width: 100%;
                        height: 100%;
                        object-fit: cover;
                    }

                    .refresh-icon {
                        position: absolute;
                        top: 0;
                        left: 0;
                        width: 100%;
                        height: 100%;
                        background: rgba(0, 0, 0, 0.3);
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        opacity: 0;
                        transition: opacity 0.3s ease;

                        svg {
                            width: 20px;
                            height: 20px;
                        }
                    }
                }
            }
        }
    }

    .form-options {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 25px;

        .remember-me {
            display: flex;
            align-items: center;
            font-size: 13px;
            color: var(--gray);
            cursor: pointer;
            position: relative;
            transition: color 0.3s ease;

            input {
                position: absolute;
                opacity: 0;
                cursor: pointer;
                height: 0;
                width: 0;

                &:checked~.checkmark {
                    background-color: var(--primary);
                    border-color: var(--primary);

                    &::after {
                        display: block;
                    }
                }
            }

            .checkmark {
                position: relative;
                height: 16px;
                width: 16px;
                background-color: var(--light-gray);
                border: 1px solid rgba(94, 92, 92, 0.89);
                border-radius: 4px;
                margin-right: 8px;
                transition: all 0.2s ease;

                &::after {
                    content: "";
                    position: absolute;
                    display: none;
                    left: 5px;
                    top: 2px;
                    width: 4px;
                    height: 8px;
                    border: solid white;
                    border-width: 0 2px 2px 0;
                    transform: rotate(45deg);
                }
            }

            &:hover input~.checkmark {
                border-color: var(--primary-light);
            }
        }

        .forgot-password {
            font-size: 13px;
            color: var(--primary);
            text-decoration: none;
            transition: color 0.2s ease;

            &:hover {
                color: var(--secondary);
            }
        }
    }

    .error-message {
        color: var(--error);
        font-size: 13px;
        padding: 12px 15px;
        background: rgba(247, 37, 133, 0.1);
        border-radius: 8px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        opacity: 0;
        height: 0;
        overflow: hidden;
        transition: all 0.3s ease;

        svg {
            width: 16px;
            height: 16px;
            margin-right: 8px;
        }

        &.show {
            opacity: 1;
            height: auto;
        }
    }

    .login-button {
        width: 100%;
        padding: 16px;
        background: linear-gradient(to right,
                var(--primary) 0%,
                var(--primary-light) 100%);
        border: none;
        border-radius: 10px;
        font-size: 15px;
        font-weight: 500;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(67, 97, 238, 0.3);
        position: relative;
        overflow: hidden;

        span {
            position: relative;
            z-index: 2;
        }

        svg {
            width: 16px;
            height: 16px;
            position: relative;
            z-index: 2;
            transition: transform 0.3s ease;
        }

        &::before {
            content: "";
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(to right,
                    var(--secondary) 0%,
                    var(--primary) 100%);
            transition: all 0.4s ease;
        }

        &:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(67, 97, 238, 0.4);

            &::before {
                left: 0;
            }

            svg {
                transform: translateX(4px);
            }
        }

        &:active {
            transform: translateY(0);
            box-shadow: 0 5px 15px rgba(67, 97, 238, 0.3);
        }
    }
}

.social-login {
    margin: 30px 0;
    text-align: center;

    p {
        font-size: 13px;
        color: var(--gray);
        margin-bottom: 15px;
        position: relative;
        transition: color 0.3s ease;

        &::before,
        &::after {
            content: "";
            position: absolute;
            top: 50%;
            width: 30%;
            height: 1px;
            background: rgba(0, 0, 0, 0.1);
            transition: background 0.3s ease;
        }

        &::before {
            left: 0;
        }

        &::after {
            right: 0;
        }
    }

    .social-icons {
        display: flex;
        justify-content: center;
        gap: 15px;

        .social-icon {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s ease;
            border: 1px solid rgba(0, 0, 0, 0.1);
            background: var(--light-gray);

            svg {
                width: 18px;
                height: 18px;
            }

            &.google {
                color: #db4437;

                &:hover {
                    background: #db4437;
                    color: white;
                    transform: translateY(-3px);
                    box-shadow: 0 5px 15px rgba(219, 68, 55, 0.3);
                }
            }

            &.github {
                color: var(--dark);

                &:hover {
                    background: var(--dark);
                    color: white;
                    transform: translateY(-3px);
                    box-shadow: 0 5px 15px rgba(33, 37, 41, 0.3);
                }
            }

            &.twitter {
                color: #1da1f2;

                &:hover {
                    background: #1da1f2;
                    color: white;
                    transform: translateY(-3px);
                    box-shadow: 0 5px 15px rgba(29, 161, 242, 0.3);
                }
            }
        }
    }
}

.login-footer {
    text-align: center;
    font-size: 14px;
    color: var(--gray);
    margin-top: auto;
    transition: color 0.3s ease;

    .footer-link {
        color: var(--primary);
        text-decoration: none;
        font-weight: 500;
        transition: color 0.2s ease;

        &:hover {
            color: var(--secondary);
        }
    }
}

@media (max-width: 992px) {
    .login-container {
        width: 90%;
        height: 100%;
        flex-direction: column;
    }

    .login-left,
    .login-right {
        width: 100%;
        padding: 40px;
    }

    .login-left {
        padding-bottom: 30px;
    }

    .login-right {
        padding-top: 30px;
    }
}

@media (max-width: 576px) {
    .login-container {
        width: 95%;
    }

    .login-left,
    .login-right {
        padding: 30px 20px;
    }

    .form-group.captcha-group .captcha-input {
        flex-direction: column;

        .captcha-image {
            width: 100%;
        }
    }
}

@media (max-height: 1000px) {
    .login-left {
        display: none;
    }
}
</style>
