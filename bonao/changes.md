# Change Log

## 2026-04-09
- File: final/complete_gui.py
- Scope: parse_and_add_courses matching logic
- Changes:
  - Added Unicode-safe normalization helper to treat PHU and PHU (with diacritics) equivalently.
  - Added robust token extraction for pasted lines copied from table-like text.
  - Reworked fuzzy matching to precompute normalized class entries and strongly prioritize subject prefix.
  - Removed per-line warning popup inside loop; unmatched lines are now summarized at the end.
- Reason: Fix false negative parsing and wrong-match behavior when class names contain Vietnamese diacritics or inconsistent separators.

## 2026-04-12
- File: final/complete_gui.py
- Scope: SePay payment detection
- Changes:
  - Tightened transfer matching to require the full MASV digits in SePay content.
  - Removed the truncated-content fallback that allowed shortened transfer notes to pass.
- Reason: Payment verification should only succeed when the transfer content includes the complete student ID.

- File: final/complete_gui.py
- Scope: transfer note display
- Changes:
  - Added a single transfer-note string source and bound it to the entered MASV.
  - Fixed the retry message so it renders the real `ULSA <MASV>` value instead of a literal placeholder.
- Reason: The QR/text prompt must show the exact note the user should transfer with.

- File: final/build_exe_bao_mat.bat
- Scope: secure EXE packaging script
- Changes:
  - Forced the build to use the project .venv Python instead of the global PATH interpreter.
  - Added a hard stop when .venv is missing to avoid rebuilding in a polluted system environment.
- Reason: Keep the protected build isolated from the system Python and remove dependency noise.

- File: build_exe_smart.ps1
- Scope: smart EXE packaging script
- Changes:
  - Anchored the build to the script directory so it finds the correct venv, requirements, and spec file.
  - Aligned the expected output exe name with the PyInstaller spec output.
- Reason: Prevent the build from silently using the wrong working directory or checking the wrong output file.

- File: build_exe_smart.ps1
- Scope: PowerShell syntax compatibility
- Changes:
  - Removed non-ASCII output strings so the script parses correctly in Windows PowerShell 5.1.
  - Kept the build flow ASCII-only to avoid encoding-dependent parse failures.
- Reason: Fix the actual parser error caused by encoding-sensitive console strings.

- File: final/complete_gui.py
- Scope: cloud version gate
- Changes:
  - Changed update logic from "cloud version must be newer" to "cloud version must match exactly".
  - Fail-closed when GitHub version cannot be verified, instead of silently allowing the app to continue.
- Reason: Force update whenever the app version differs from the GitHub version.

## 2026-04-13
- File: final/automation/auto_login_with_title_check.py
- Scope: post-login redirect to course registration page
- Changes:
  - Relaxed success URL detection from exact `SinhVien.aspx?Chuyen_nganh=1` to broader `SinhVien.aspx` marker.
  - Added a reload cap (`max_reload_attempts = 20`) to prevent endless refresh loops.
  - Wrapped `driver.refresh()` with page-load timeout handling to avoid blocking when the portal hangs.
  - Added fallback behavior to force navigation to B1 after repeated retries.
  - Wrapped `driver.get(B1)` with timeout handling so the flow can continue even when the target page loads slowly.
- Reason: fix the case where automation gets stuck loading at `SinhVien.aspx` and never proceeds to the registration page.

- File: automation/auto_login_with_title_check.py
- Scope: source-flow parity with final build
- Changes:
  - Mirrored the same URL matching and timeout-safe navigation improvements from `final/automation`.
- Reason: keep local source runs and final build behavior consistent for troubleshooting.

- File: automation/auto_login_with_title_check.py
- Scope: hard redirect from SinhVien/ChangePassword to B1
- Changes:
  - Added `force_redirect_to_b1()` with retry logic using both `driver.get` and JavaScript `window.location` fallback.
  - Replaced all direct `driver.get(target_course_url)` calls in login and F5/retry flows with the new forced redirect helper.
  - Redirect now treats B1/B2/B3 URLs as success markers to avoid false failures when the site auto-advances.
- Reason: eliminate the stuck-loading state at `SinhVien.aspx` / `ChangePassword.aspx` and guarantee progression to registration flow.

- File: final/automation/auto_login_with_title_check.py
- Scope: parity hard redirect fix for final runtime
- Changes:
  - Applied the same `force_redirect_to_b1()` logic and call-site replacements as source automation.
- Reason: ensure packaged/final runtime has the same non-stuck redirect behavior as source runtime.

- File: final/complete_gui.py
- Scope: app/cloud version alignment
- Changes:
  - Updated `APP_VERSION` from `4.9` to `4.8`.
- Reason: cloud config on GitHub requires `4.8`; exact-version gate blocks mismatched builds.

- File: final/complete_gui.py
- Scope: forced upgrade wave
- Changes:
  - Updated `APP_VERSION` from `4.8` to `5.0`.
- Reason: prepare a new release line so all older clients can be forced to update when cloud version is set to 5.0.

- File: automation/auto_login_with_title_check.py
- Scope: **CRITICAL FIX** - prevent jumping to B1 when still on Login page
- Changes:
  - **ADDED conditional check**: Only proceed to B1 if `url_matched == True` (successfully reached SinhVien.aspx OR ChangePassword.aspx).
  - **ADDED fail condition**: If reload loop completes but URL still doesn't match (still on Login.aspx), immediately return False instead of jumping to B1.
  - Updated log messages to clearly indicate:
    - ❌ "LỖI: Không bắt được URL đích..." when stuck on Login
    - ✅ "URL CHÍNH XÁC" only when one of the 2 success URLs is confirmed
  - Restructured printing to prevent fall-through behavior.
- Reason: **CRITICAL BUG FIX** - Previous code had infinite logic error:
  - While loop reloads waiting for SinhVien.aspx OR ChangePassword.aspx
  - If URL never changes from Login.aspx, reload loop exits
  - **BUT THEN** code fell through and jumped to B1 anyway (without checking if url_matched was True)
  - This caused the "vô hạn đoạn login" (infinite login) behavior user reported
  - Now: Only jumps to B1 after **CONFIRMING** one of the 2 URLs is achieved
  
- File: final/automation/auto_login_with_title_check.py
- Scope: **CRITICAL FIX** - mirror fail-closed logic
- Changes:
  - Applied identical conditional guard before B1 navigation as source automation.
- Reason: ensure final/packaged build has same fail-closed protection against jumping to B1 too early.

- File: automation/auto_login_with_title_check.py + final/automation/auto_login_with_title_check.py
- Scope: reload attempt limit
- Changes:
  - **REMOVED** `max_reload_attempts` entirely.
  - **CHANGED** to `while not url_matched:` (NO condition check - truly infinite).
- Reason: Reload liên tục mà không giới hạn cho đến khi nó tự chuyển sang SinhVien.aspx hoặc ChangePassword.aspx.

- File: final/complete_gui.py
- Scope: app version bump
- Changes:
  - Updated `APP_VERSION` from `5.0` to `5.1`.
- Reason: Release version with enhanced course search (diacritics fix).

- File: final/complete_gui.py
- Scope: app version bump
- Changes:
  - Updated `APP_VERSION` from `5.1` to `5.2`.
- Reason: Release a new build line after the course search fix.

- File: final/complete_gui.py
- Scope: app version bump
- Changes:
  - Updated `APP_VERSION` from `5.2` to `5.3`.
- Reason: Package a new patch release as requested.

- File: automation/auto_login_with_title_check.py + final/automation/auto_login_with_title_check.py
- Scope: course search failure with Vietnamese diacritics (Đ issue)
- Changes:
  - **ADDED** `normalize_text_for_search()` function: strips diacritics, trims whitespace, converts to uppercase
    - Example: "TĐTC0122L" → "TDTC0122L" (remove the diacritical mark on Đ)
  - **ENHANCED** `select_courses_on_page()`: added JavaScript-based page content dump (debug output showing all text on page, showing normalized versions)
  - **ENHANCED** `find_and_select_course()`: 
    * **Method 1 (PRIMARY)**: Ctrl+F-style JavaScript search on page text, with Unicode normalization at browser level
    * **Method 2 (FALLBACK)**: Original XPath selectors if text search fails
    * Added detailed logging showing "Normalized khi tìm: 'TĐTC0122L' → 'TDTC0122L'"
    * Fixed `course_selectors` scope crash when JS search found the text first
  - **RESULT**: Courses with Vietnamese diacritics like "TĐTC0122L" will now be found reliably, and text that is already visible on the page is matched like browser Ctrl+F
- Reason: **CRITICAL FIX** - Previous code failed to match course names containing Vietnamese diacritics (Đ) because XPath normalize-space() doesn't remove accents, only XPath whitespace. Script would report "Không tìm thấy TĐTC0122L" even though it existed on page. Now: JavaScript Ctrl+F-style search normalizes page text correctly and then resolves the matching element safely.

- File: automation/auto_login_with_title_check.py + final/automation/auto_login_with_title_check.py
- Scope: B1 -> B2 transition and B2 class-only search
- Changes:
  - Added `wait_for_b2_url_after_b1_button()` to enforce transition after `cmdDangKyLop2` on B1.
  - After auto/manual click in B1, script now waits until URL contains `wfrmDangKyLopTinChiB2.aspx` before continuing.
  - Updated B2 config fallback to avoid searching by B1 subject codes:
    - uses only class-like entries (`.` or `_LT/_TH/_BT`) from legacy list.
- Reason: Fix wrong flow where script could continue without truly reaching B2, and prevent B2 from searching course names instead of class names.

- File: automation/auto_login_with_title_check.py + final/automation/auto_login_with_title_check.py
- Scope: B3 no-reload-when-correct + stronger Vietnamese matching
- Changes:
  - Updated `wait_for_b3_title_and_url()` to accept URL by marker (`wfrmDangKyLopTinChiB3.aspx`) instead of exact-equals.
  - Removed blocking ENTER prompt after reaching correct B3 state.
  - Updated normalization for search:
    - Python: map `Đ/đ` to `D/d` before NFD cleanup.
    - JavaScript (Ctrl+F-style matcher): map `Đ/đ` to `D` before accent removal.
- Reason: When B3 URL had query string (`?Chuyen_nganh=1`) exact URL compare caused unnecessary reload loops, and some Vietnamese codes with `Đ` could mismatch during search.

## 2026-04-14
- File: automation/auto_login_with_title_check.py + final/automation/auto_login_with_title_check.py
- Scope: B3 immediate pause when title is correct
- Changes:
  - Replaced strict B3 URL string check with URL marker `wfrmDangKyLopTinChiB3.aspx` in the affected B2->B3 transition block.
  - Changed success condition in reload loop: if B3 title is valid, stop reload immediately.
  - Removed secondary "title đúng nhưng URL chưa đúng" reload loop; now it pauses all actions instead of refreshing.
  - Added explicit log: "Title B3 đã đúng, tạm dừng toàn bộ hành động và KHÔNG reload thêm".
- Reason: User reported continuous `Reload #n để vào B3` even when B3 title was already correct; requested hard stop with no further action.

## 2026-04-13 (Continued)
- File: automation/auto_login_with_title_check.py + final/automation/auto_login_with_title_check.py
- Scope: **CRITICAL FIX** - Remove dangerous "first checkbox fallback" causing wrong courses selected
- Changes:
  - **REMOVED** automatic fallback to `checkboxes[0]` when no exact match found in parent row.
  - **REMOVED** automatic selection of "closest by position" checkbox when no exact value/name/id match exists.
  - **CHANGED** both methods to log debug info instead, without selecting a checkbox.
  - Now only returns a checkbox if:
    - Exact match found by `value`, `name`, or `id` containing the course code
    - OR the method explicitly validates the checkbox is related to the requested course
  - For table row method: validate checkbox value/name contains the course code before returning
- Reason: **CRITICAL BUG FIX** - Previous code would select the first checkbox in a row even if it belonged to a different course (e.g., selecting TDTT0122H when looking for PTTC0123H). This caused:
  - False "already_selected" reports (checkbox was selected but for wrong course)
  - Wrong courses being registered
  - Partial/failed course selection operations
  Now: Script only selects checkboxes with confirmed exact matches, returns "not_found" if no match, allowing user to manually select or try again.

## 2026-04-13 (Final Session Update)
- File: automation/auto_login_with_title_check.py + final/automation/auto_login_with_title_check.py
- Scope: **MAJOR FIX** - Checkbox/Radio selection logic rewritten for portal HTML structure
- Root Cause Identified:
  - **B3 Page**: Checkboxes have **NO value attribute** (analyzed actual HTML provided by user)
  - **B2 Page**: Radio buttons have **NO value attribute** containing class name
  - Course code is in a **sibling `<td>` element** in the same table row, not in the input itself
  - Previous approach tried to match course code in checkbox/radio value/name/id - always failed
  - Example B3: `<input id="grdViewMonDangKy_ctl02_chk">` has no value containing "BOR11421T"
  - Example B2: `<input id="grd_ctl02_chk" type="radio" name="31463LT">` radio button in same row as course name
- Changes Made:
  - **New Primary Method**: Find parent `<tr>` row from `course_element`, then find checkbox/radio in that row
    - Uses XPath: `./ancestor::tr[1]` to navigate up to parent row
    - Uses XPath: `.//input[@type='checkbox']` for B3 or `.//input[@type='radio']` for B2
    - Prioritizes checkbox (B3) first, then radio (B2) if no checkbox found
  - **Secondary Methods**: Parent element XPath selectors with proper upward navigation
    - Supports both checkbox and radio button types
    - Tries multiple levels: parent, grandparent, great-grandparent
  - **Tertiary Method**: Table row XPath to find rows containing course code text
    - Searches for checkbox first (B3 mode), then radio button (B2 mode)
  - **Removed All Pattern Matching**: No longer tries to find course code in input value/name/id
  - **Removed All Fallbacks**: No auto-selection of first checkbox/radio or nearest-by-distance
  - Returns `None` if input cannot be found, allowing script to report "not_found"
- Result:
  - ✅ Correct checkbox selection on B3 based on row position (same row as course code visual)
  - ✅ Correct radio button selection on B2 based on row position (same row as class name visual)
  - ✅ No false "already_selected" reports from wrong inputs
  - ✅ No accidental selection of wrong courses/classes
  - ✅ Clear error reporting when input cannot be located
- Testing Notes:
  - Both source and final versions have identical fixes
  - Syntax verified - no Python errors
  - Ready for user to test on both B2 (class selection) and B3 (review/confirmation) pages

## 2026-04-13 (Wait Loop Hotfix)
- File: automation/auto_login_with_title_check.py + final/automation/auto_login_with_title_check.py
- Scope: B1 manual-click wait loop stuck even after user clicked
- Root Cause:
  - Wait loop only exited when `driver.current_url` changed.
  - On this portal, clicking button can trigger postback/update while URL stays unchanged.
  - Result: log keeps printing `Dang cho...` for many minutes even though user already clicked.
- Changes:
  - Updated B1 manual wait loop to exit on either:
    - URL changed, OR
    - B2 DOM detected (`//table[@id='grd']//input[@type='radio']`).
  - Updated `wait_for_b2_url_after_b1_button()` success condition to accept either:
    - URL contains `wfrmDangKyLopTinChiB2.aspx`, OR
    - B2 DOM marker detected (radio list in table `grd`).
  - Kept reload fallback when neither URL nor DOM indicates B2.
- Result:
  - Bot no longer hangs in manual wait when user clicked but URL did not change.
  - Transition B1 -> B2 is robust for both full navigation and same-URL postback cases.

## 2026-04-13 (B2 Wait Loop Hotfix)
- File: automation/auto_login_with_title_check.py + final/automation/auto_login_with_title_check.py
- Scope: B2 manual-click wait after "Lưu kết quả đăng ký" stuck even after user clicked
- Root Cause:
  - `wait_for_b3_after_save_button()` step 1 relied on URL/title changes only.
  - Portal can postback with same URL, so click happened but loop kept waiting.
  - Step 2 also required strict URL string check, missing B3 detection in same-URL or query-variant cases.
- Changes:
  - Replaced strict B3 URL with marker: `wfrmDangKyLopTinChiB3.aspx`.
  - Step 1 (wait user click): now exits if either:
    - URL/title changed, OR
    - B3 DOM detected (`//table[@id='grdViewMonDangKy']//input[@type='checkbox']`).
  - Step 2 (wait until reached B3): success when:
    - Title valid, and
    - URL marker matched OR B3 DOM marker matched.
  - Added debug logs to show when DOM-B3 was used as transition signal.
- Result:
  - B2 recognizes manual click immediately even with same-URL postback.
  - No more long "Đang chờ..." loop after user already clicked save.

## 2026-04-13 (Wait Log Throttling)
- File: automation/auto_login_with_title_check.py + final/automation/auto_login_with_title_check.py
- Scope: Reduce noisy waiting logs while keeping wait behavior unchanged
- Changes:
  - In 0.5s polling wait loop, status print frequency changed from every 2s to every 600s (10 minutes).
    - `check_count % 4 == 0` -> `check_count % 1200 == 0`
  - In 1s polling wait loop, waiting print frequency changed from every 10s to every 600s (10 minutes).
    - `wait_count % 10 == 0` -> `wait_count % 600 == 0`
- Result:
  - Same waiting logic and detection behavior.
  - Console output is much cleaner; waiting messages appear only every 10 minutes.

## 2026-04-13 (Auto-Click Logic & Wait Loop Detection)
- File: automation/auto_login_with_title_check.py + final/automation/auto_login_with_title_check.py
- Scope: **Implement proper auto-click logic + improved wait loop feedback**
- Root Cause:
  - B1 had auto-click but logs were throttled (no feedback for 10 minutes)
  - B2 had broken auto-click with wrong button ID (used B1's `cmdDangKyLop2`)
  - Wait loops didn't give user real-time feedback on whether click was detected
- Behavior (Now Fixed):
  - **B1**: Đủ môn → Tự bấm "Đăng ký lớp tín chỉ"; Thiếu → Chờ user bấm
  - **B2**: Đủ lớp → Tự bấm "Lưu kết quả đăng ký"; Thiếu → Chờ user bấm
  - **Detection**: Script knows when user clicked by monitoring URL + DOM markers (every 0.5s poll)
  - **Feedback**: Status updates every 5 seconds so user knows it's not stuck
- Changes Made:
  - **B1 manual wait** (`handle_page_b1` wait loop):
    - Changed sleep from `1s` to `0.5s` for faster detection.
    - Changed log frequency from `600s` intervals to `5s` intervals (`10 % 10 == 0`).
    - Shows elapsed time in seconds and current URL preview.
    - Print message when B2 DOM is detected (shows count of radio buttons).
    - New output: `⏳ Đang chờ... (5.0s) | URL hiện tại: https://...`
  - **B1->B2 transition** (`wait_for_b2_url_after_b1_button()`):
    - Changed sleep from `1.5s/1s` to `0.5s` for faster polling.
    - Added log frequency control: logs every `5s` intervals instead of every loop.
    - Print message showing elapsed time in seconds.
    - Shows URL preview (first 70 chars) for debugging.
    - Print debug output when B2 radio buttons are detected.
    - New output: `🔍 B1→B2 check #10 (5.0s): URL = https://...`
  - **B2 auto-click** (`handle_page_b2` auto-click logic):
    - Fixed: Replaced hardcoded `click_submit_button("cmdDangKyLop2", ...)` with robust XPath search
    - Method 1: Submit input with normalized Vietnamese text match (handles diacritics: À→A)
    - Method 2: Button element containing "Lưu" text (Ctrl+F style)
    - Method 3: Fallback scan all submit inputs, pick one with "Lưu" in value
    - Uses JavaScript `execute_script()` for reliable click (avoids Selenium click() issues)
    - If auto-click succeeds → Wait 2s then check B3 conditions
    - If auto-click fails → Shows "Manual click required" message and enters wait loop
    - Same detection as B1: waits for URL change OR B3 DOM marker detection
  - **Result**:
    - ✅ B1 & B2 both auto-click when all courses/classes found
    - ✅ B1 & B2 both wait gracefully when missing items (with user feedback every 5s)
    - ✅ Detection uses URL markers + DOM + real-time polling (0.5-1s intervals)
    - ✅ Console output shows elapsed time so user knows system is active
    - Changed sleep from `1.5s/1s` to `0.5s` for faster polling.
    - Added log frequency control: logs every `5s` intervals instead of every loop.
    - Print message showing elapsed time in seconds.
    - Shows URL preview (first 70 chars) for debugging.
    - Print debug output when B2 radio buttons are detected.
    - New output: `🔍 B1→B2 check #10 (5.0s): URL = https://...`
- Result:
  - User now sees feedback every 5 seconds (instead of 10+ minutes).
  - Clear visibility when DOM detection succeeds.
  - Can verify if portal is responding or stuck.
  - If button click fails, user will know within 5 seconds instead of sitting blind.
- Testing Impact:
  - Polling remains correct (0.5s intervals, same detection logic).
  - Only logging frequency increased (5s instead of 600s).
  - DOM detection unchanged (still checks for `table#grd` radio buttons).
  - Both source and final versions synchronized.

