// jobos/middleware.ts
export { authGuard as middleware } from "./app/src/middleware/authGuard";

export const config = {
  matcher: ["/dashboard/:path*"],
};
