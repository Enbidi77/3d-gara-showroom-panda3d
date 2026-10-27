"""Tests for Vehicle Catalog, search, sorting, and favorites."""


import pytest

from panda_motors.vehicles.vehicle_catalog import VehicleCatalog


@pytest.fixture
def catalog():
    return VehicleCatalog()


def test_catalog_loads_vehicles(catalog):
    vehicles = catalog.get_all()
    assert len(vehicles) >= 6
    ids = [v.id for v in vehicles]
    assert "panda_corsa_gt" in ids
    assert "aventador_svj" in ids
    assert "porsche_911_gt3" in ids


def test_get_vehicle_by_id(catalog):
    v = catalog.get_vehicle("panda_corsa_gt")
    assert v is not None
    assert v.display_name == "Panda Corsa 750 GT"
    assert v.specifications.power_hp == 740
    assert v.specifications.accel_0_100 == 2.8


def test_filter_by_category(catalog):
    supercars = catalog.get_by_category("Supercars")
    assert len(supercars) >= 1
    assert any(v.id == "panda_corsa_gt" for v in supercars)

    all_cars = catalog.get_by_category("All Cars")
    assert len(all_cars) == len(catalog.get_all())


def test_search_vehicles(catalog):
    catalog.search("Ferrari")
    # Searches either brand, model, or description
    res_corsa = catalog.search("Corsa")
    assert len(res_corsa) >= 1
    assert res_corsa[0].id == "panda_corsa_gt"

    res_hyper = catalog.search("Apex")
    assert len(res_hyper) >= 1
    assert res_hyper[0].id == "aventador_svj"


def test_sort_vehicles(catalog):
    all_veh = catalog.get_all()
    # Sort by power descending
    by_power = catalog.sort_by(all_veh, "power")
    for i in range(len(by_power) - 1):
        assert by_power[i].specifications.power_hp >= by_power[i + 1].specifications.power_hp

    # Sort by acceleration ascending (fastest first)
    by_accel = catalog.sort_by(all_veh, "accel")
    for i in range(len(by_accel) - 1):
        assert by_accel[i].specifications.accel_0_100 <= by_accel[i + 1].specifications.accel_0_100


def test_favorites(catalog):
    vid = "panda_corsa_gt"
    assert not catalog.is_favorite(vid)
    catalog.toggle_favorite(vid)
    assert catalog.is_favorite(vid)
    favs = catalog.get_favorites()
    assert any(v.id == vid for v in favs)

    catalog.toggle_favorite(vid)
    assert not catalog.is_favorite(vid)


def test_compare_vehicles(catalog):
    cmp = catalog.compare_vehicles(["panda_corsa_gt", "aventador_svj"])
    assert len(cmp) == 2
    assert cmp[0].id == "panda_corsa_gt"
    assert cmp[1].id == "aventador_svj"
