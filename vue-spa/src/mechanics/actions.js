import anime from 'animejs'

class ActionManager {
    constructor(board) {
        this.board = board;
//        this.actionParams = {
////        some values, passed in constructor, for example
//            'length_of_path_of_fire': 4
//        }
        this.currentAction = null;
        this.actionData = {};
        this.animation_elements = this.board.svg.group();

        this.actions = {
            move: {
                set: () => {
                    this.actionData.path = [];
                    this.board.hero.updateHandler = this.actions.move.heroUpdateHandler;
                    for (var hex_id in this.board.grid.hexes) {
                        this.board.grid.hexes[hex_id].clickHandler = this.actions.move.hexClickHandler;
                    }
                    for (var unit_id in this.board.units) {
                        this.board.units[unit_id].clickTargetHandler = this.actions.move.unitClickHandler;
                    }
                },
                drop: () => {
                    this.board.hero.updateHandler = null;
                    this.actions.move.resetPath();
                    this.actionData = {};
                },
                buildPath: destination => {
                    this.actionData.path = this.board.grid.findPath(this.board.hero.hex, destination);
                    this.actionData.path.forEach(hex => {
                        hex.polygon.classList.add('path');
                    })
                },
                resetPath: () => {
                    if ('path' in this.actionData) {
                        this.actionData.path.forEach(hex => {
                            hex.polygon.classList.remove('path');
                        })
                    }
                    this.actionData.path = [];
                },
                heroUpdateHandler: () => {
                    this.actions.move.resetPath();
                },
                hexClickHandler: hex => {
                    if (this.currentAction != 'move') {
                        this.changeAction('move');
                    }
                    if (this.board.grid.distance(hex, this.board.hero.hex) <= this.board.hero.move_range) {
                        this.actions.move.resetPath();
                        this.board.component.requestAction({'action': 'move', 'destination': hex.q + ';' + hex.r});
                    } else {
                        this.actions.move.goLongPath(hex);
                    }
                },
                unitClickHandler: unit => {
                    if (this.board.grid.distance(unit.hex, this.board.hero.hex) <= this.board.hero.attack_range) {
                        this.board.component.requestAction({'action': 'attack', 'target': unit.pk});
                    } else if (this.board.grid.distance(unit.hex, this.board.hero.hex) <= this.board.hero.attack_range + 1) {
                        this.board.component.requestAction({'action': 'range_attack', 'target': unit.pk});
                    } else {
                        this.actions.move.goLongPath(unit.hex);
                    }
                },
                goLongPath: hex => {
                    if ('path' in this.actionData && this.actionData.path.length > 0) {
                        if (hex != this.actionData.path[0]) {
                            this.actions.move.resetPath();
                            this.actions.move.buildPath(hex);
                        } else {
                            let hex_in_path = this.actionData.path[this.actionData.path.length - 1];
                            this.board.component.requestAction({'action': 'move',
                                                                'destination': hex_in_path.q + ';' + hex_in_path.r});
                        }
                    } else {
                        this.actions.move.buildPath(hex);
                    }
                }
            },
            attack: {
                set: () => {
                    this.actions.attack.setByAttackHexes(this.board.hero.attack_hexes);
                },
                setByAttackHexes: attackHexes => {
                    this.actionData.targets = [];
                    for (var unit_id in this.board.units) {
                        let unit = this.board.units[unit_id];
                        if (attackHexes.includes(unit.hex.q + ';' + unit.hex.r)) {
                            this.actionData.targets.push(unit);
                            unit.hex.polygon.classList.add('availableAttackTarget');
                            unit.overTargetHandler = this.actions.attack.unitMouseoverHandler;
                            unit.outTargetHandler = this.actions.attack.unitMouseoutHandler;
                        }
                    }
                },
                drop: () => {
                    this.actionData.targets.forEach(unit => {
                        unit.hex.polygon.classList.remove('availableAttackTarget');
                        unit.hex.polygon.classList.remove('attackTarget');
                        unit.overTargetHandler = null;
                        unit.outTargetHandler = null;
                    })
                    this.actionData = {};
                },
                unitMouseoverHandler: hex => {
                    hex.polygon.classList.remove('availableAttackTarget');
                    hex.polygon.classList.add('attackTarget');
                },
                unitMouseoutHandler: hex => {
                    hex.polygon.classList.remove('attackTarget');
                    hex.polygon.classList.add('availableAttackTarget');
                }
            },
            range_attack: {
                set: () => {
                    this.actions.attack.setByAttackHexes(this.board.hero.range_attack_hexes);
                },
                drop: () => {
                    this.actions.attack.drop()
                }
            },
//            spells
            'Path of fire': {
                set: () => {
                    this.actionData.target_hexes = this.board.grid.getHexesInRange(this.board.hero.hex, 1, ['empty', 'unit']);
                    this.actionData.target_hexes.forEach(hex_id => {
                        let hex = this.board.grid.hexes[hex_id];
                        hex.polygon.classList.add('spellTarget');
                        hex.overTargetHandler = this.actions['Path of fire'].mouseover;
                        hex.outTargetHandler = this.actions['Path of fire'].mouseout;
                        hex.clickHandler = this.actions['Path of fire'].clickHandler;
                    });
                    this.actionData.target_units = [];
                    for (var unit_id in this.board.units) {
                        let unit = this.board.units[unit_id];
                        if (this.actionData.target_hexes.includes(unit.hex.q + ';' + unit.hex.r)) {
                            this.actionData.target_units.push(unit);
                            unit.overTargetHandler = this.actions['Path of fire'].mouseover;
                            unit.outTargetHandler = this.actions['Path of fire'].mouseout;
                            unit.clickTargetHandler = this.actions['Path of fire'].clickHandler;
                        }
                    }
                    this.actionData.path = [];
                },
                drop: () => {
                    this.actionData.target_hexes.forEach(hex_id => {
                        let hex = this.board.grid.hexes[hex_id];
                        hex.polygon.classList.remove('spellTarget');
                        hex.overTargetHandler = null;
                        hex.outTargetHandler = null;
                        hex.clickHandler = null;
                    });
                    this.actionData.target_units.forEach(unit => {
                        unit.overTargetHandler = null;
                        unit.outTargetHandler = null;
                        unit.clickTargetHandler = null;
                    });
                    this.actionData.path.forEach(_hex => {
                        _hex.polygon.classList.remove('pathOfFire');
                    });
                    this.actionData = {};
                },
                mouseover: hex => {
                    let dq = hex.q - this.board.hero.hex.q;
                    let dr = hex.r - this.board.hero.hex.r;
                    for (var i = 1; i < 5; i++) {
                        let current_hex = this.board.grid.getHexByCoords(this.board.hero.hex.q + dq * i,
                                                                         this.board.hero.hex.r + dr * i);
                        if (current_hex === undefined || current_hex.occupied_by == 'obstacle') {
                            break;
                        }
                        this.actionData.path.push(current_hex);
                    }
                    this.actionData.path.forEach(_hex => {
                        _hex.polygon.classList.add('pathOfFire');
                    });
                },
                mouseout: hex => {
                    this.actionData.path.forEach(_hex => {
                        _hex.polygon.classList.remove('pathOfFire');
                    });
                    this.actionData.path = [];
                },
                clickHandler: hex => {
                    this.board.component.requestAction({'action': 'path_of_fire', 'target_hex': hex.polygon.id});
                },
                actionHandler: actionData => {
                    let animation = anime.timeline({
                        complete: (anim) => {
                            this.animation_elements.clear();
                        }
                    });

                    for (var i = 0; i < actionData.target_hexes.length; i++) {
                        let hex = this.board.grid.hexes[actionData.target_hexes[i]];
                        let {x, y} = hex.toPoint();
                        let explosion = this.animation_elements.image('./src/assets/path_of_fire_explosion.png', 60, 60);
                        animation.add({
                            targets: explosion.node,
                            duration: 0,
                            opacity: 0,
                            translateX: x + 30,
                            translateY: y + 30,
                            scale: 0.1
                        }).add({
                            targets: explosion.node,
                            opacity: 1,
                            scale: 1,
                            translateX: x,
                            translateY: y,
                            easing: 'easeOutQuart',
                            duration: 200
                        }, 75*i).add({
                            targets: explosion.node,
                            opacity: 0,
                            duration: 100
                        });
                    }
                    for (var unit_id in actionData.targets) {
                        this.board.units[unit_id].getDamage(actionData.targets[unit_id].damage);
                    }
                }
            }
        }
    }

    dropCurrentAction() {
        this.actions[this.currentAction].drop();
    }

    setAction(actionName) {
        this.currentAction = actionName;
        this.actions[actionName].set();
    }

    changeAction(actionName) {
        if (this.currentAction != actionName) {
            console.log('Action changed:', this.currentAction, '->', actionName);
            this.dropCurrentAction();
            this.setAction(actionName);
        }
    }

    handleAction(actionData) {
        if (actionData.action == 'path_of_fire') {
            actionData.action = 'Path of fire';
        }
        if ('actionHandler' in this.actions[actionData.action]) {
            this.actions[actionData.action].actionHandler(actionData);
        }
    }
}

export default ActionManager
