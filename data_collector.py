from Proj5GUI import Proj5GUI

if __name__ == "__main__":
    n_cities = [15, 30, 60, 100, 200]
    time_limit_seconds = 600
    gui = Proj5GUI()
    gui.generateNetwork()
    s = gui.solver


    algorithms_to_test = [s.defaultRandomTour, s.greedy, s.branchAndBound, s.two_swap_local_search, s.local_search_tournament]
    for n in n_cities:
        gui.diffDropDown.setCurrentIndex(2)
        print(gui.diffDropDown.currentText())
        gui.size.setText(f"{n}")
