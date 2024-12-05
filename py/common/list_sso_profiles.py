def list_sso_profiles():
  """List available AWS SSO profiles."""
  import subprocess
  try:
    result = subprocess.run(
      ["aws", "configure", "list-profiles"],
      stdout=subprocess.PIPE,
      text=True,
      check=True
    )
    return result.stdout.strip().split("\n")
  except Exception as e:
    print(f"Error listing SSO profiles: {e}")
    return []