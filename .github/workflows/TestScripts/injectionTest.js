const input = process.argv[2];

// Simple check to simulate testing for script injection
if (input.includes("<script>")) {
  console.error("Potential script injection detected!");
  process.exit(1); // Exit with a failure status
} else {
  console.log("No script injection detected.");
  process.exit(0); // Exit with a success status
}
