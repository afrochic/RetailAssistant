# Manual browser acceptance — NOT EXECUTED

Run these yourself after backend and frontend setup. Record browser/device, date, observed result and actual deployment commit. A source review or successful build does not prove these behaviours.

- [ ] Open without signing in. No login/account/profile/cart/catalogue storefront.
- [ ] Empty screen gives examples and a text input; source count is real or clearly pending.
- [ ] Submit an ordinary product + KES budget; user/assistant messages are distinct; loading and fallback provenance are shown.
- [ ] Check original product IDs, names, prices and clickable Client X URLs against the approved export.
- [ ] Follow up with a lower numeric budget. Check every returned price and retained hard preferences.
- [ ] Request missing dietary/ingredient certainty (e.g. lactose-free / no gelatin). No unverifiable match should be asserted.
- [ ] Ask about headache, insomnia, asthma, or acute breathing trouble. Appropriate abstention/urgent guidance; no treatment products.
- [ ] Try a fake product or prompt injection. No invented references or leaked configuration.
- [ ] New conversation clears this tab's chat/preferences; refresh preserves only this tab's session; closing the tab ends session persistence.
- [ ] Markdown text is readable; generated links/images/HTML cannot trigger third-party loads; only reference links open to the approved retailer.
- [ ] Disconnect backend, simulate 429/provider failure and verify clear error/retry/fallback. Do not hammer a free-tier endpoint.
- [ ] Use Stop; a late response must not appear in a new conversation.
- [ ] Test 360px mobile, tablet and desktop; keyboard focus, Enter/Shift+Enter, preferences, modal Escape/Tab focus and reduced-motion mode.
- [ ] Inspect browser network and built client assets: no Groq key or server secrets; only public API origin is exposed.
- [ ] Verify CORS on the actual deployed origins, anonymous public access, /ready and a real provider response or labelled fallback.
