<h2>SliceAndJoinGcode – Cura Plugin</h2>

<p><strong>Version:</strong> 51<br>
<strong>Date:</strong> 13.01.2026</p>

<h4>Supported Cura version: 5.11.0</h4>

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
      <li>Search &amp; replace functionality</li>
    </ul>
  </li>
</ul>

<h2>Why This Plugin Is Needed</h2>

<p>
By default, Cura is commonly used with <strong>Wall Ordering = Inside → Outside</strong>.
While this works well in most cases, problems can occur when the first layer contains many
small features, such as grids, meshes, or perforated surfaces.
</p>

<p>
With <strong>Inside → Outside</strong> ordering, Cura prints the smallest parts of the first
layer first. These tiny segments often have very little contact area with the build plate
and may not adhere properly, causing them to detach during printing.
</p>

<p>
When the first layer is printed with <strong>Wall Ordering = Outside → Inside</strong>,
the outer walls and larger areas are printed first. Small features are printed last, allowing
them to adhere not only to the build plate but also to already printed material.
</p>

<p>
This results in a more reliable and visually cleaner first layer, with fewer gaps, fewer
adhesion failures, and a significantly reduced risk of small segments lifting from the build
plate.
</p>

<p>
The SliceAndJoinGcode plugin automates this process by combining the best of both approaches:
<strong>Outside → Inside</strong> for the first layer, and <strong>Inside → Outside</strong>
for all remaining layers.
</p>

<h2>Features</h2>

<ul>
  <li>Slices the first layer <strong>Outside → Inside</strong></li>
  <li>Slices all other layers <strong>Inside → Outside</strong></li>
  <li>Automatically merges the two G-code outputs</li>
  <li>Displays merged G-code in a dialog window</li>
  <li>Search &amp; Replace (case-insensitive) inside the G-code</li>
  <li>Dark theme with G-code syntax highlighting</li>
  <li>Compatible with Cura 5.11.x</li>
  <li>Default G-code filename format: <code>XXXXXX_modelname.gcode</code><br>
      <small>(XXXXXX = first 6 letters of the active printer’s name)</small>
  </li>
</ul>

<h2>How It Works</h2>

<ul>
  <li>Slices the first layer <strong>Outside → Inside</strong></li>
  <li>Slices all other layers <strong>Inside → Outside</strong></li>
  <li>Automatically merges the two G-code outputs</li>
  <li>Displays merged G-code in a dialog window</li>
  <li>Search &amp; Replace (case-insensitive) inside the G-code</li>
  <li>Dark theme with G-code syntax highlighting</li>
  <li>Compatible with Cura 5.11.x</li>
  <li>Default G-code filename format: <code>XXXXXX_modelname.gcode</code></li>
  <li><small>(XXXXXX = first 6 letters of the active printer's name)</small></li>
</ul>

<h2>Installation</h2>

<ul>
  <li><strong>Download</strong> the latest version:
      <code>SliceAndJoinGcode_v51.curapackage</code></li>
  <li><strong>Open</strong> Cura 5.11.x</li>
  <li><strong>Drag &amp; drop</strong> the <code>.curapackage</code> file into the Cura window</li>
  <li><strong>Restart</strong> Cura</li>
  <li>The plugin will appear in the <strong>Extensions</strong> menu as
      <em>"Slice First Layer Outside-In"</em></li>
</ul>

<h2>Usage</h2>

<ul>
  <li><strong>Load</strong> your model onto the build plate</li>
  <li><strong>Open</strong> the plugin from
      <code>Extensions → Slice First Layer Outside-In → Run</code></li>
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

<p>
This plugin is released under the <strong>AGPL-3.0 License</strong>.<br>
You are free to use, modify, and redistribute it under the terms of the license.
Commercial use requires compliance with AGPL-3.0.
</p>

<h2>Screenshots</h2>

<img
  src="https://github.com/user-attachments/assets/af2406ef-0449-43e3-b428-2bc318812a9d"
  alt="SliceAndJoinGcode G-code Viewer"
  width="1128"
  height="792"
/>
