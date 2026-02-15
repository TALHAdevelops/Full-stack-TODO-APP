import { betterAuth } from "better-auth"
import { username } from "better-auth/plugins/username"

export const auth = betterAuth({
    baseURL: process.env.NEXT_PUBLIC_APP_URL,
    secret: process.env.BETTER_AUTH_SECRET,
    advanced: {
        cookiePrefix: "taskflow",
    },
    plugins: [
        username({
            usernameValidator: () => true,
        }),
    ],
})
