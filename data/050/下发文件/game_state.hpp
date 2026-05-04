#pragma once

#include <array>
#include <exception>
#include <optional>

class InvalidOperation : public std::exception {
public:
    const char* what() const noexcept override {
        return "invalid operation";
    }
};

struct PlayInfo {
    int dummyCount = 0;
    int magnifierCount = 0;
    int converterCount = 0;
    int cageCount = 0;
};

class GameState {
public:
    enum class BulletType { Live, Blank };
    enum class ItemType { Dummy, Magnifier, Converter, Cage };

    GameState() {
        // TODO
    }

    void fireAtOpponent(BulletType topBulletBeforeAction) {
        // TODO:
    }
    void fireAtSelf(BulletType topBulletBeforeAction) {
        // TODO:
    }
    void useDummy(BulletType topBulletBeforeUse) {
        // TODO
    }
    void useMagnifier(BulletType topBulletBeforeUse) {
        // TODO
    }
    void useConverter(BulletType topBulletBeforeUse) {
        // TODO
    }
    void useCage() {
        // TODO
    }
    void reloadBullets(int liveCount, int blankCount) {
        // TODO
    }
    void reloadItem(int playerId, ItemType item) {
        // TODO
    }
    double nextLiveBulletProbability() const {
        // TODO
        return 1.0;
    }
    double nextBlankBulletProbability() const {
        // TODO
        return 1.0;
    }

    int winnerId() const {
        // TODO
        return -1;        
    }
private:
    // TODO
};
