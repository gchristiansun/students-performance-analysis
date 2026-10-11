from pathlib import Path

import joblib
import pandas as pd
import plotly.express as px
import streamlit as st


DATA_URL = (
	"https://raw.githubusercontent.com/dicodingacademy/dicoding_dataset/"
	"main/students_performance/data.csv"
)
MODEL_PATH = Path(__file__).resolve().parent / "model" / "model.joblib"
FEATURES = [
	"Age_at_enrollment",
	"Tuition_fees_up_to_date",
	"Scholarship_holder",
	"Debtor",
	"Curricular_units_1st_sem_enrolled",
	"Curricular_units_1st_sem_approved",
	"Curricular_units_1st_sem_grade",
	"Curricular_units_2nd_sem_enrolled",
	"Curricular_units_2nd_sem_approved",
	"Curricular_units_2nd_sem_grade",
]
STATUS_COLORS = {
	"Graduate": "#198754",
	"Dropout": "#d94841",
	"Enrolled": "#e0a526",
}

st.set_page_config(
	page_title="Jaya Jaya Institut | Student Success",
	layout="wide",
)


@st.cache_data(ttl=3600)
def load_data():
	return pd.read_csv(DATA_URL, sep=";", encoding="utf-8-sig")


@st.cache_resource
def load_model():
	return joblib.load(MODEL_PATH)


try:
	students = load_data()
	model = load_model()
except Exception as error:
	st.error(f"Data atau model tidak dapat dimuat. Periksa file dan koneksi internet. Detail: {error}")
	st.stop()

st.title("Jaya Jaya Institut")
st.caption("Student success monitoring - cohort dataset 2008-2019")
page = st.sidebar.radio("Ruang kerja", ["Dashboard", "Prediksi risiko"])

if page == "Dashboard":
	st.subheader("Ringkasan performa siswa")
	st.caption(
		"Profil kohort historis. Dataset tidak memiliki ID siswa maupun dimensi waktu "
		"per semester, sehingga visual ini bukan pemantauan longitudinal real-time."
	)

	with st.sidebar:
		st.markdown("#### Filter kohort")
		selected_status = st.multiselect(
			"Status akhir", sorted(students["Status"].unique()),
			default=sorted(students["Status"].unique()),
		)
		gender_codes = sorted(students["Gender"].unique().tolist())
		selected_gender = st.multiselect(
			"Kode gender", gender_codes, default=gender_codes
		)
		age_min, age_max = int(students["Age_at_enrollment"].min()), int(
			students["Age_at_enrollment"].max()
		)
		age_range = st.slider(
			"Usia saat mendaftar", age_min, age_max, (age_min, age_max)
		)

	filtered = students[
		students["Status"].isin(selected_status)
		& students["Gender"].isin(selected_gender)
		& students["Age_at_enrollment"].between(*age_range)
	]
	if filtered.empty:
		st.info("Tidak ada siswa yang cocok dengan filter ini.")
	else:
		total = len(filtered)
		dropout_rate = filtered["Status"].eq("Dropout").mean()
		graduate_rate = filtered["Status"].eq("Graduate").mean()
		tuition_current = filtered["Tuition_fees_up_to_date"].eq(1).mean()
		metric_cols = st.columns(4)
		metric_cols[0].metric("Siswa dalam filter", f"{total:,}")
		metric_cols[1].metric("Dropout", f"{dropout_rate:.1%}")
		metric_cols[2].metric("Lulus", f"{graduate_rate:.1%}")
		metric_cols[3].metric("Biaya kuliah aktif", f"{tuition_current:.1%}")

		chart_left, chart_right = st.columns(2)
		with chart_left:
			outcomes = filtered["Status"].value_counts().rename_axis("Status").reset_index(
				name="Jumlah"
			)
			st.plotly_chart(
				px.pie(
					outcomes,
					names="Status",
					values="Jumlah",
					hole=0.52,
					color="Status",
					color_discrete_map=STATUS_COLORS,
					title="Komposisi status akhir",
				),
				use_container_width=True,
			)
		with chart_right:
			semester_grades = filtered.melt(
				id_vars="Status",
				value_vars=[
					"Curricular_units_1st_sem_grade",
					"Curricular_units_2nd_sem_grade",
				],
				var_name="Semester",
				value_name="Nilai rata-rata",
			)
			semester_grades["Semester"] = semester_grades["Semester"].map(
				{
					"Curricular_units_1st_sem_grade": "Semester 1",
					"Curricular_units_2nd_sem_grade": "Semester 2",
				}
			)
			grade_summary = semester_grades.groupby(
				["Status", "Semester"], as_index=False
			)["Nilai rata-rata"].mean()
			st.plotly_chart(
				px.bar(
					grade_summary,
					x="Status",
					y="Nilai rata-rata",
					color="Semester",
					barmode="group",
					title="Rata-rata nilai per semester dan status",
					color_discrete_sequence=["#2364aa", "#e07a35"],
				),
				use_container_width=True,
			)

		academic = filtered.groupby("Status", as_index=False).agg(
			**{
				"Rata-rata unit lulus S1": (
					"Curricular_units_1st_sem_approved", "mean"
				),
				"Rata-rata unit lulus S2": (
					"Curricular_units_2nd_sem_approved", "mean"
				),
			}
		)
		st.plotly_chart(
			px.bar(
				academic.melt("Status", var_name="Periode", value_name="Unit lulus"),
				x="Status",
				y="Unit lulus",
				color="Periode",
				barmode="group",
				title="Unit kurikulum yang berhasil diselesaikan",
				color_discrete_sequence=["#2364aa", "#e07a35"],
			),
			use_container_width=True,
		)

		completed_outcomes = filtered[
			filtered["Status"].isin(["Dropout", "Graduate"])
		]
		if completed_outcomes["Status"].nunique() < 2:
			st.info(
				"Analisis faktor memerlukan data Dropout dan Graduate. "
				"Pilih kedua status pada filter kohort."
			)
		else:
			factor_definitions = {
				"Tunggakan": ("Debtor", {0: "Tidak", 1: "Ya"}),
				"Pembayaran kuliah": (
					"Tuition_fees_up_to_date",
					{0: "Belum tercatat lunas", 1: "Tercatat lunas"},
				),
				"Beasiswa": (
					"Scholarship_holder",
					{0: "Tanpa beasiswa", 1: "Dengan beasiswa"},
				),
			}
			factor_summaries = []
			for factor_name, (column_name, category_labels) in factor_definitions.items():
				factor_summary = (
					completed_outcomes.assign(
						Kelompok=completed_outcomes[column_name].map(category_labels)
					)
					.groupby("Kelompok", as_index=False, observed=True)
					.agg(
						**{
							"Tingkat Dropout": (
								"Status",
								lambda status: status.eq("Dropout").mean(),
							),
							"Jumlah siswa": ("Status", "size"),
						}
					)
				)
				factor_summary["Faktor"] = factor_name
				factor_summary["Kategori"] = (
					factor_name + ": " + factor_summary["Kelompok"]
				)
				factor_summaries.append(factor_summary)

			factor_risk = pd.concat(factor_summaries, ignore_index=True)
			academic_groups = completed_outcomes.assign(
				**{
					"Kelompok capaian": pd.cut(
						completed_outcomes["Curricular_units_2nd_sem_approved"],
						bins=[-1, 2, 5, float("inf")],
						labels=["0-2 unit lulus", "3-5 unit lulus", "6+ unit lulus"],
					)
				}
			)
			academic_risk = (
				academic_groups.groupby("Kelompok capaian", as_index=False, observed=True)
				.agg(
					**{
						"Tingkat Dropout": (
							"Status",
							lambda status: status.eq("Dropout").mean(),
						),
						"Jumlah siswa": ("Status", "size"),
					}
				)
			)

			chart_left, chart_right = st.columns(2)
			with chart_left:
				factor_chart = px.bar(
					factor_risk,
					x="Tingkat Dropout",
					y="Kategori",
					color="Faktor",
					orientation="h",
					text_auto=".1%",
					hover_data={"Jumlah siswa": True, "Kelompok": False},
					title="Tingkat Dropout menurut faktor administrasi",
					color_discrete_sequence=["#d94841", "#2364aa", "#e0a526"],
				)
				factor_chart.update_xaxes(tickformat=".0%", range=[0, 1])
				factor_chart.update_layout(
					xaxis_title="Proporsi Dropout di dalam kelompok",
					yaxis_title=None,
					legend_title="Faktor",
				)
				st.plotly_chart(factor_chart, use_container_width=True)
			with chart_right:
				academic_chart = px.bar(
					academic_risk,
					x="Kelompok capaian",
					y="Tingkat Dropout",
					text_auto=".1%",
					hover_data={"Jumlah siswa": True},
					title="Tingkat Dropout menurut unit lulus semester 2",
					color_discrete_sequence=["#d94841"],
				)
				academic_chart.update_yaxes(tickformat=".0%", range=[0, 1])
				academic_chart.update_layout(
					xaxis_title="Jumlah unit lulus",
					yaxis_title="Proporsi Dropout",
				)
				st.plotly_chart(academic_chart, use_container_width=True)

			st.caption(
				f"Analisis faktor memakai {len(completed_outcomes):,} siswa Dropout/Graduate "
				"dalam filter; Enrolled tidak dimasukkan ke penyebut. "
				"Hubungan yang terlihat bersifat deskriptif, bukan bukti sebab-akibat."
			)

		st.plotly_chart(
			px.histogram(
				filtered,
				x="Age_at_enrollment",
				color="Status",
				barmode="overlay",
				opacity=0.72,
				nbins=20,
				color_discrete_map=STATUS_COLORS,
				title="Distribusi usia saat mendaftar",
			),
			use_container_width=True,
		)

		with st.expander("Lihat data kohort terfilter"):
			st.dataframe(filtered, use_container_width=True, hide_index=True)
			st.download_button(
				"Unduh data terfilter sebagai CSV",
				filtered.to_csv(index=False).encode("utf-8"),
				file_name="jaya_jaya_kohort_terfilter.csv",
				mime="text/csv",
			)

else:
	st.subheader("Estimasi risiko dropout")
	st.write(
		"Masukkan ringkasan siswa hingga semester kedua. Model memprediksi status "
		"Dropout (1) dibandingkan Graduate (0); hasil adalah sinyal untuk ditinjau "
		"oleh dosen pembimbing, bukan keputusan otomatis."
	)
	with st.form("student_risk_form"):
		first, second = st.columns(2)
		with first:
			age = st.number_input("Usia saat mendaftar", 17, 70, 22)
			tuition_paid = st.checkbox("Biaya kuliah tercatat lunas", value=True)
			scholarship = st.checkbox("Penerima beasiswa")
			debtor = st.checkbox("Memiliki tunggakan")
			enrolled_1 = st.number_input("Unit diambil - semester 1", 0, 30, 6)
			approved_1 = st.number_input("Unit lulus - semester 1", 0, 30, 4)
		with second:
			grade_1 = st.number_input("Nilai rata-rata - semester 1", 0.0, 20.0, 10.0)
			enrolled_2 = st.number_input("Unit diambil - semester 2", 0, 30, 6)
			approved_2 = st.number_input("Unit lulus - semester 2", 0, 30, 4)
			grade_2 = st.number_input("Nilai rata-rata - semester 2", 0.0, 20.0, 10.0)
		submitted = st.form_submit_button("Hitung estimasi", type="primary")

	if submitted:
		student = pd.DataFrame(
			[[
				age,
				int(tuition_paid),
				int(scholarship),
				int(debtor),
				enrolled_1,
				approved_1,
				grade_1,
				enrolled_2,
				approved_2,
				grade_2,
			]],
			columns=FEATURES,
		)
		risk = model.predict_proba(student)[0, 1]
		st.metric("Estimasi probabilitas dropout", f"{risk:.1%}")
		if risk >= 0.5:
			st.warning(
				"Risiko model berada pada kategori tinggi. Tinjau kemajuan akademik "
				"dan kendala siswa secara langsung sebelum menentukan tindak lanjut."
			)
		else:
			st.success(
				"Risiko model berada di bawah ambang 50%. Tetap pantau kemajuan "
				"akademik dan kondisi siswa secara berkala."
			)
		st.caption(
			"Model dilatih hanya dengan siswa berstatus Dropout dan Graduate "
			"menggunakan fitur semester 1–2; siswa Enrolled tidak menjadi data training. "
			"Estimasi ini bukan probabilitas kausal dan belum menggantikan validasi "
			"serta evaluasi berkala sebelum penggunaan operasional."
		)
