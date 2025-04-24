// jobos/middleware.ts
export { authGuard as middleware } from "./src/middleware/authGuard";

export const config = {
  matcher: ["/dashboard/:path*"],
};
