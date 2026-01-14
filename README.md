<h2>SliceAndJoinGcode – Cura Plugin</h2>

Version: 51
Date: 13.01.2026

<h2>Overview</h2>

<ul>
  <li>SliceAndJoinGcode is a Cura plugin that prepares G-code in a unique way.</li>
  <li>The first layer is printed <strong>Outside → Inside</strong>.</li>
  <li>All subsequent layers are printed <strong>Inside → Outside</strong>.</li>
  <li>This approach helps:
    <ul>
      <li>Improve first layer adhesion</li>
      <li>Enhance surface quality</li>
      <li>Maintain printing consistency in the first layer</li>
      <li>Preserve normal printing behavior for remaining layers</li>
    </ul>
  </li>
  <li>The plugin also includes a feature-rich G-code viewer with:
    <ul>
      <li>Syntax highlighting</li>
      <li>Dark theme support</li>
      <li>Search & replace functionality</li>
    </ul>
  </li>
</ul>

<h2>Features</h2>

Slices the first layer Outside → Inside
Slices all other layers Inside → Outside
Automatically merges the two G-code outputs
Displays merged G-code in a dialog window
Search & Replace (case-insensitive) inside the G-code
Dark theme with G-code syntax highlighting
Compatible with Cura 5.11.x
Default G-code filename format: XXXXXX_modelname.gcode
(XXXXXX = first 6 letters of the active printer’s name)

<h2>How It Works</h2>

<ul>
  <li>Slices the first layer <strong>Outside → Inside</strong></li>
  <li>Slices all other layers <strong>Inside → Outside</strong></li>
  <li>Automatically merges the two G-code outputs</li>
  <li>Displays merged G-code in a dialog window</li>
  <li>Search & Replace (case-insensitive) inside the G-code</li>
  <li>Dark theme with G-code syntax highlighting</li>
  <li>Compatible with Cura 5.11.x</li>
  <li>Default G-code filename format: <code>XXXXXX_modelname.gcode</code></li>
  <li><small>(XXXXXX = first 6 letters of the active printer's name)</small></li>
</ul>

<h2>Installation</h2>

<ul>
  <li><strong>Download</strong> the latest version: <code>SliceAndJoinGcode_v51.curapackage</code></li>
  <li><strong>Open</strong> Cura 5.11.x</li>
  <li><strong>Drag & drop</strong> the <code>.curapackage</code> file into the Cura window</li>
  <li><strong>Restart</strong> Cura</li>
  <li>The plugin will appear in the <strong>Extensions</strong> menu as <em>"Slice First Layer Outside-In"</em></li>
</ul>

<h2>Usage</h2>

<ul>
  <li><strong>Load</strong> your model onto the build plate</li>
  <li><strong>Open</strong> the plugin from <code>Extensions → Slice First Layer Outside-In → Run</code></li>
  <li>The plugin will automatically slice your model:
    <ul>
      <li>First layer <strong>Outside → Inside</strong></li>
      <li>Remaining layers <strong>Inside → Outside</strong></li>
    </ul>
  </li>
  <li>After slicing, a dialog will display the merged G-code</li>
  <li>Use the <strong>Search</strong> and <strong>Replace</strong> fields as needed</li>
  <li>Click <strong>Save G-code</strong> to save the file</li>
</ul>

<h2>Notes</h2>

<ul>
  <li>The plugin disables <strong>Auto Slice</strong> during processing and restores it afterward</li>
  <li>The G-code viewer supports syntax highlighting for:
    <ul>
      <li><code>G</code> commands</li>
      <li><code>M</code> commands</li>
      <li><code>X</code>, <code>Y</code>, <code>Z</code> coordinates</li>
      <li><code>E</code> (extrusion) values</li>
      <li><code>F</code> (feedrate) values</li>
      <li><code>S</code> (parameter) values</li>
    </ul>
  </li>
  <li><strong>Dark theme</strong> is applied by default for better readability</li>
</ul>

<h2>License</h2>

This plugin is released under the AGPL-3.0 License.
You are free to use, modify, and redistribute it under the terms of the license, but commercial use requires compliance with AGPL-3.0.


<img width="1128" height="792" alt="image" src="https://github.com/user-attachments/assets/af2406ef-0449-43e3-b428-2bc318812a9d" />
