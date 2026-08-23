with open(r"C:\IEMS\static\css\workspace.css", "r", encoding="utf-8") as f:
    content = f.read()

css_to_add = """
.card-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

@media (max-width: 767px) {
  .card-grid, .detail-grid, .audit-grid {
    grid-template-columns: 1fr !important;
  }
}
"""

if ".card-grid {" not in content:
    with open(r"C:\IEMS\static\css\workspace.css", "a", encoding="utf-8") as f:
        f.write("\n" + css_to_add)
    print("Added card-grid responsive CSS.")
else:
    print("card-grid already exists.")
