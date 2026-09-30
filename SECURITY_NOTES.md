Password storage
•	Storage: SQLite users table
•	Password field example: scrypt:32768:8:1$SYxXXuy01KOEZfMA$579b16bf...d3501
•	Interpretation: scrypt hash with explicit parameters and random per-user salt; no plaintext passwords stored.
•	Conclusion: Safe password storage

JWT
•	Test: no authorization header
•	Expected: request rejected, no data returned
•	Observed: 401 UNAUTHORIZED + "Missing Authorization Header"
•	Conclusion: Authentication barrier holds; nmissing authorization headers are rejected before route logic.

•	Test: malformed/bogus JWT
•	Expected: request rejected, no data returned
•	Observed: 422 UNPROCESSABLE ENTITY, error parsing header, no recipes returned
•	Conclusion: Authentication barrier holds; malformed tokens are rejected before route logic.

Invalid JWT tests
•	No token: GET /recipes → 401, "Missing Authorization Header" → clear authentication failure ✅
•	Malformed / bogus tokens: both this.is.not.a.real.token and a JWT-shaped string → 422 UNPROCESSABLE ENTITY with parsing /
    padding errors, no data returned ✅
•	Conclusion: API never treats invalid tokens as authenticated; protected data is not exposed.

Ownership authorization
•	Owner (Alice) can read and update her own recipe (200 OK, state changes).
•	Non-owner (Bob) gets 403 FORBIDDEN "access denied" on PATCH and DELETE.
•	Conclusion: Ownership checks work for both modification and deletion; no cross-user exploit.
