1.	POST /auth/login — never cache
    auth-sensitive, per-user, and high-impact if leaked or reused
2.	POST /recipes/ (and other POSTs) — never cache
    change state and are not idempotent
3.	GET routes — generally safe to cache, EXCEPT:
    •	GET /me or GET /users/<id> when it depends on who’s logged in
    •	GET /recipes if it includes private recipes based on auth
    •	Any GET that represents very fresh/real-time data (e.g., “current balance”, “live score”) where stale data is unacceptable

GET /recipes originally required a header with a JWT that included the current user and it used this
to determine if some non public recipes appeared in the list if teh current user owned those recipes.
This requirement was removed leaving the route public only and able to be cached.  If the JWT requirement
is ever reinstated then caching needs to be removed / or disabled.

GET /recipes is the only route at the moment that uses caching.
