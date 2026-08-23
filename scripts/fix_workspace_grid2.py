with open(r"C:\IEMS\static\css\workspace.css", "a", encoding="utf-8") as f:
    f.write("\n" + """
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
""")
print("Appended successfully.")
