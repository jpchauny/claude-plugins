# recap

Gets you back into a session after time away: `/recap:recap` writes, in the
chat, a short report of the session it is invoked from — its goal, what was
done, the decisions taken, and what is pending to do or decide. Only that session: not the project's history, not other sessions.

Install it once per person, at user scope; it is not enabled in any project:

```sh
claude plugin install recap@jpchauny-plugins --scope user
```
