import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

print("directory actuel :", os.getcwd())


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    ref = pd.read_csv(os.getcwd() +
                      "/2024-assignment-pandas/data/referendum.csv", sep=";")
    regions = pd.read_csv(os.getcwd() +
                          "/2024-assignment-pandas/data/regions.csv", sep=",")
    departements = pd.read_csv(os.getcwd() +
                               "/2024-assignment-pandas" +
                               "/data/departments.csv",
                               sep=",")
    return ref, regions, departements


def merge_regions_and_departments(regions, departements):
    regions.columns = ["id", "region_code", "name_reg", "slug"]
    departements.columns = ["id", "region_code",
                            "Department code", "name_dep", "slug"]
    return pd.DataFrame(pd.merge(regions.iloc[:, 1:3],
                        departements.iloc[:, 1:4],
                        how='right',
                        on=["region_code"]))


def merge_ref_and_areas(ref, reg_and_dep):
    liste_domtom = ['01', '02', '03', '04', '06', 'COM']
    liste_refer_domtom = ['ZA', 'ZB', 'ZC', 'ZD',
                          'ZM', 'ZN', 'ZP', 'ZS', 'ZW', 'ZX', 'ZZ']
    reg_dep_metropole = reg_and_dep.iloc[
                                         [i for
                                          i in
                                          range(reg_and_dep.shape[0])
                                          if
                                          reg_and_dep.iloc[i, 0]
                                          not in liste_domtom]]
    referendum_metropole = ref.iloc[[i
                                     for i in range(ref.shape[0])
                                     if ref.iloc[i, 0] not in
                                     liste_refer_domtom]]
    for k in range(1, 10):
        intermed = referendum_metropole['Department code'].replace(str(k),
                                                                   '0'+str(k))
        referendum_metropole['Department code'] = intermed
    return pd.DataFrame(pd.merge(reg_dep_metropole, referendum_metropole,
                        how='right', on=["Department code"]))


def compute_ref_result_by_regions(ref_and_areas):
    reg_area_intermed = ref_and_areas[
                                      ['region_code', 'Registered',
                                       'Abstentions',
                                       'Null', 'Choice A', 'Choice B']
                                        ].groupby('region_code' +
                                                  '').sum(
                                                          ).reset_index()
    reg_name_intermed = ref_and_areas[["region_code",
                                       "name_reg"]].drop_duplicates()
    reg_area_final = pd.merge(reg_name_intermed,
                              reg_area_intermed, on=["region_code"])
    reg_area_final.index = reg_area_final["region_code"]
    reg_area_final = reg_area_final.drop("region_code", axis=1)
    return reg_area_final


def plot_referendum_map(referendum_result_by_regions):
    geographic_data = gpd.read_file(os.getcwd() +
                                    "/2024-assignment-pandas" +
                                    "/data/regions.geojson")
    geographic_data.index = geographic_data["code"]
    geographic_data = geographic_data.drop("code", axis=1)
    ref_results = pd.merge(referendum_result_by_regions,
                           geographic_data, left_index=True,
                           right_index=True)
    ref_results["ratio"] = ref_results["Choice A"]/(
                                       ref_results["Choice A"] +
                                       ref_results["Choice B"])
    ref_results = gpd.GeoDataFrame(ref_results)
    plt.figure()
    ref_results.plot("ratio", cmap="coolwarm")
    plt.title('ratio de votes effectifs pour le candidat A')
    return gpd.GeoDataFrame(ref_results)


if __name__ == "__main__":
    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(
                                                            df_reg, df_dep
                                                            )
    referendum_and_areas = merge_ref_and_areas(
                                               referendum,
                                               regions_and_departments
                                               )
    referendum_results = compute_ref_result_by_regions(
                                                       referendum_and_areas
                                                       )
    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()
