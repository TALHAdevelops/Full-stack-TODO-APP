import { NextResponse } from "next/server";
import jwt from "jsonwebtoken";

export async function GET(request: Request) {
  // Try to get token from Authorization header first, then from cookie
  const authHeader = request.headers.get("authorization");
  let token = authHeader?.replace("Bearer ", "");

  if (!token) {
    // Fallback: get token from cookie
    const cookieHeader = request.headers.get("cookie") || "";
    const tokenMatch = cookieHeader.match(/auth_token=([^;]+)/);
    token = tokenMatch?.[1];
  }

  if (!token) {
    return NextResponse.json({ session: null, user: null }, { status: 401 });
  }

  try {
    const secret = process.env.BETTER_AUTH_SECRET!;
    const decoded = jwt.verify(token, secret) as { sub: string };

    // Fetch user from backend
    const userRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/users/${decoded.sub}`);
    if (!userRes.ok) {
      return NextResponse.json({ session: null, user: null }, { status: 401 });
    }

    const user = await userRes.json();

    return NextResponse.json({
      session: {
        token,
        expiresAt: new Date(Date.now() + 30 * 60 * 1000).toISOString(),
      },
      user: {
        id: user.id,
        email: user.email,
        name: user.name,
        emailVerified: false,
      },
    });
  } catch (error) {
    return NextResponse.json({ session: null, user: null }, { status: 401 });
  }
}
