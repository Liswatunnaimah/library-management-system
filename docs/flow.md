flowchart TB
%% =========================================================
%% Library Management System - One Big Program Flow (stable, colored)
%% - Tanpa label di edge (semua teks jadi nama node) -> parser lebih aman
%% - Re-prompt, "0 batal", guards, dan export tetap direpresentasikan
%% =========================================================

%% === START & MAIN MENU ===
START([Mulai Program]) --> MENU{{Main Menu}}
MENU --> READ
MENU --> CREATE
MENU --> UPDATE
MENU --> DELETE
MENU --> BORROW
MENU --> REPORT
MENU --> ANALYTICS
MENU --> END([Selesai])

%% === READ MENU ===
READ[Read Data] --> RD_ALL["Read: Tampilkan semua"]
READ --> RD_ID["Read: Cari by ID (0 batal)"]
READ --> RD_EXACT["Read: Filter exact (0 batal)"]
READ --> RD_KEY["Read: Keyword search (0 batal)"]
READ --> MENU

RD_ALL --> READ

%% re-prompt & hasil
RD_ID --> RD_ID_ERR["ID non-angka / tidak ada → re-prompt"] --> RD_ID
RD_ID --> RD_SHOW["Tampilkan detail buku"] --> READ

RD_EXACT --> RD_EXACT_ERR["Kolom/nilai invalid → re-prompt"] --> RD_EXACT
RD_EXACT --> RD_RES["Tampilkan hasil filter"] --> READ

RD_KEY --> RD_KEY_ERR["Kosong / tidak ada hasil → re-prompt"] --> RD_KEY
RD_KEY --> RD_RES2["Tampilkan hasil keyword"] --> READ

%% === CREATE MENU ===
CREATE[Create Data] --> C_J["Create: Input judul (0 batal)"]
C_J --> C_J_BTL["Batal → kembali"] --> MENU
C_J --> C_P["Create: Input penulis (0 batal)"]
C_P --> C_P_BTL["Batal → kembali"] --> MENU
C_P --> C_PB["Create: Input penerbit (0 batal)"]
C_PB --> C_PB_BTL["Batal → kembali"] --> MENU
C_PB --> C_T["Create: Input tahun (0 batal)"]

C_T --> C_T_ERR["Tahun non-angka / <1450 / >tahun berjalan → re-prompt"] --> C_T
C_T --> C_CF{"Create: Konfirmasi simpan?"}
C_CF --> C_CF_NO["Tidak"] --> CREATE
C_CF --> C_SAVE["Simpan buku -> books.json"] --> CREATE
CREATE --> MENU

%% === UPDATE MENU ===
UPDATE[Update Data] --> U_ID["Update: Input ID (0 batal)"]
U_ID --> U_ID_BTL["Batal → kembali"] --> MENU
U_ID --> U_ID_ERR["Non-angka / ID tidak ada → re-prompt"] --> U_ID
U_ID --> U_COL{"Pilih field: judul / penulis / penerbit / tahun"}
U_COL --> U_COL_ERR["Pilihan invalid → re-prompt"] --> U_COL
U_COL --> U_VAL["Update: Input nilai baru (0 batal)"]
U_VAL --> U_VAL_BTL["Batal → kembali"] --> UPDATE
U_VAL --> U_VAL_ERR["Tahun invalid (jika field tahun) → re-prompt"] --> U_VAL
U_VAL --> U_CF{"Konfirmasi update?"}
U_CF --> U_CF_NO["Tidak"] --> UPDATE
U_CF --> U_SAVE["Update field -> books.json"] --> UPDATE
UPDATE --> MENU

%% === DELETE MENU ===
DELETE[Delete Data] --> D_ID["Delete: Input ID (0 batal)"]
D_ID --> D_ID_BTL["Batal → kembali"] --> MENU
D_ID --> D_ID_ERR["Non-angka / ID tidak ada → re-prompt"] --> D_ID
D_ID --> D_ST{"Status buku?"}
D_ST --> D_ERR["Tolak: sedang dipinjam"] --> DELETE
D_ST --> D_CF{"Yakin hapus?"}
D_CF --> D_CF_NO["Tidak"] --> DELETE
D_CF --> D_DO["Hapus + catat -> deleted_books.json"] --> DELETE
DELETE --> MENU

%% === BORROW / RETURN MENU ===
BORROW[Borrow / Return] --> B_ID["Pinjam: Input ID (0 batal)"]
BORROW --> R_ID["Kembalikan: Input ID (0 batal)"]
BORROW --> MENU

%% Borrow flow
B_ID --> B_ID_BTL["Batal → kembali"] --> BORROW
B_ID --> B_ID_ERR["Non-angka / ID tidak ada → re-prompt"] --> B_ID
B_ID --> B_ST{"Status buku?"}
B_ST --> B_ERR["Tolak: sudah dipinjam"] --> BORROW
B_ST --> B_CF{"Konfirmasi pinjam?"}
B_CF --> B_CF_NO["Tidak"] --> BORROW
B_CF --> B_DO["Set status=borrowed + tanggal_pinjam/kembali + dipinjam+=1 -> save"] --> BORROW

%% Return flow
R_ID --> R_ID_BTL["Batal → kembali"] --> BORROW
R_ID --> R_ID_ERR["Non-angka / ID tidak ada → re-prompt"] --> R_ID
R_ID --> R_ST{"Status buku?"}
R_ST --> R_ERR["Tolak: tidak sedang dipinjam"] --> BORROW
R_ST --> R_DO["Set status=available + kosongkan tanggal -> save"] --> BORROW

BORROW --> MENU

%% === REPORT MENU ===
REPORT[Report] --> RP_SUM["Report: Lihat ringkasan (total/available/borrowed + list borrowed)"]
REPORT --> RP_EXP["Report: Export ringkasan (CSV + Chart PNG -> outputs/)"]
REPORT --> RP_TOP["Report: Export analytics Top-N (entitas + N -> CSV/XLSX/PNG)"]
REPORT --> MENU

RP_SUM --> REPORT
RP_EXP --> REPORT
RP_TOP --> REPORT

%% === ANALYTICS MENU ===
ANALYTICS[Analytics] --> AN_A["Analytics: Top-N Penulis"]
ANALYTICS --> AN_P["Analytics: Top-N Penerbit"]
ANALYTICS --> AN_J["Analytics: Top-N Judul"]
ANALYTICS --> MENU

AN_A --> AN_SHOW_A["Agregasi sum 'dipinjam' per penulis -> tampilkan tabel"] --> ANALYTICS
AN_P --> AN_SHOW_P["Agregasi sum 'dipinjam' per penerbit -> tampilkan tabel"] --> ANALYTICS
AN_J --> AN_SHOW_J["Agregasi sum 'dipinjam' per judul -> tampilkan tabel"] --> ANALYTICS

%% ========== STYLES (warna per sub-menu) ==========
classDef main fill:#f4f6f8,stroke:#2f3b52,stroke-width:1px,color:#2f3b52;
classDef read fill:#e8f5e9,stroke:#2e7d32,stroke-width:1px,color:#1b5e20;
classDef create fill:#e3f2fd,stroke:#1976d2,stroke-width:1px,color:#0d47a1;
classDef update fill:#fff8e1,stroke:#f9a825,stroke-width:1px,color:#7f6000;
classDef delete fill:#ffebee,stroke:#c62828,stroke-width:1px,color:#7f0000;
classDef borrow fill:#ede7f6,stroke:#6a1b9a,stroke-width:1px,color:#4a148c;
classDef report fill:#e0f7fa,stroke:#00838f,stroke-width:1px,color:#005662;
classDef analytics fill:#f3e5f5,stroke:#8e24aa,stroke-width:1px,color:#4a148c;

%% assign classes
class START,MENU,END main;
class READ,RD_ALL,RD_ID,RD_EXACT,RD_KEY,RD_SHOW,RD_RES,RD_RES2,RD_ID_ERR,RD_EXACT_ERR,RD_KEY_ERR read;
class CREATE,C_J,C_P,C_PB,C_T,C_CF,C_SAVE,C_J_BTL,C_P_BTL,C_PB_BTL,C_T_ERR,C_CF_NO create;
class UPDATE,U_ID,U_COL,U_VAL,U_CF,U_SAVE,U_ID_BTL,U_ID_ERR,U_COL_ERR,U_VAL_BTL,U_VAL_ERR,U_CF_NO update;
class DELETE,D_ID,D_ST,D_ERR,D_CF,D_DO,D_ID_BTL,D_ID_ERR,D_CF_NO delete;
class BORROW,B_ID,R_ID,B_ST,B_ERR,B_CF,B_DO,R_ST,R_ERR,R_DO,B_ID_BTL,B_ID_ERR,B_CF_NO,R_ID_BTL,R_ID_ERR borrow;
class REPORT,RP_SUM,RP_EXP,RP_TOP report;
class ANALYTICS,AN_A,AN_P,AN_J,AN_SHOW_A,AN_SHOW_P,AN_SHOW_J analytics;
