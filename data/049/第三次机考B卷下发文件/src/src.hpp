#ifndef PPCA_SRC_HPP
#define PPCA_SRC_HPP
#include "math.h"

class Controller {

public:
    Controller(const Vec &_pos_tar, double _v_max, double _r, int _id, Monitor *_monitor) {
        pos_tar = _pos_tar;
        v_max = _v_max;
        r = _r;
        id = _id;
        monitor = _monitor;
    }

    void set_pos_cur(const Vec &_pos_cur) {
        pos_cur = _pos_cur;
    }

    void set_v_cur(const Vec &_v_cur) {
        v_cur = _v_cur;
    }

private:
    int id;
    Vec pos_tar;
    Vec pos_cur;
    Vec v_cur;
    double v_max, r;
    Monitor *monitor;

    /////////////////////////////////
    /// TODO: You can add any [private] member variable or [private] member function you need.
    /////////////////////////////////

public:

    Vec get_v_next() {
        /// TODO: You need to decide the speed of the robot at the next moment.
        ///       You can obtain information about the robot being processed in the member variable of class Controller.
        ///       You can obtain information about the other robot by accessing the interface of *monitor.
        /// Warning: You cannot use any static variable or global variable!
        ///          You should not try to output any information!
        ///          You cannot modify any code that is not allowed to be modified!
        ///          All illegal behavior will be voided.
        return Vec();
    }
};


/////////////////////////////////
/// TODO: You can add any class or struct you need.
/////////////////////////////////


#endif //PPCA_SRC_HPP