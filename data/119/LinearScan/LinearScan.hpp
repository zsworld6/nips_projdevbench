#ifndef LINEARSCAN_HPP
#define LINEARSCAN_HPP

// don't include other headfiles
#include <string>
#include <vector>
#include <set>

class Location {
public:
    // return a string that represents the location
    virtual std::string show() const = 0;
    virtual int getId() const = 0;
};

class Register : public Location {
private:
    // do whatever you want
public:
    Register(int regId) {
        // TODO
    }
    virtual std::string show() const {
        // TODO
    }
    virtual int getId() const {
        // TODO
    }
};

class StackSlot : public Location {
public:
    StackSlot() {}
    virtual std::string show() const {
        // TODO
    }
    virtual int getId() const {
        // TODO
    }
};

struct LiveInterval {
    int startpoint;
    int endpoint;
    Location* location = nullptr;
};

class LinearScanRegisterAllocator {
private:
    // add necessary member variables and functions here

    void expireOldIntervals(LiveInterval& i) {
        // TODO
    }
    void spillAtInterval(LiveInterval& i) {
        // TODO
    }
public:
    LinearScanRegisterAllocator(int regNum) {
        // TODO
    }
    void linearScanRegisterAllocate(std::vector<LiveInterval>& intervalList) {
        // TODO
    }
};

#endif
