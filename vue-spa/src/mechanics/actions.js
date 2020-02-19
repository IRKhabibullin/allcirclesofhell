import anime from 'animejs'

class ActionManager {
    constructor(board) {
        this.board = board;
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
                        this.board.component.requestAction({'action': 'move', 'target_hex': hex.q + ';' + hex.r});
                    } else {
                        this.actions.move.goLongPath(hex);
                    }
                },
                unitClickHandler: unit => {
                    if (this.board.grid.distance(unit.hex, this.board.hero.hex) <= this.board.hero.attack_range) {
                        this.board.component.requestAction({'action': 'attack', 'target_hex': unit.hex.q + ';' + unit.hex.r});
                    } else if (this.board.grid.distance(unit.hex, this.board.hero.hex) <= this.board.hero.attack_range + 1) {
                        this.board.component.requestAction({'action': 'range_attack', 'target_hex': unit.hex.q + ';' + unit.hex.r});
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
                                                                'target_hex': hex_in_path.q + ';' + hex_in_path.r});
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
                    this.actionData.target_units = [];
                    for (var unit_id in this.board.units) {
                        let unit = this.board.units[unit_id];
                        if (attackHexes.includes(unit.hex.q + ';' + unit.hex.r)) {
                            this.actionData.target_units.push(unit);
                            unit.hex.polygon.classList.add('availableAttackTarget');
                            unit.overTargetHandler = this.actions.attack.unitMouseoverHandler;
                            unit.outTargetHandler = this.actions.attack.unitMouseoutHandler;
                        }
                    }
                },
                drop: () => {
                    this.actionData.target_units.forEach(unit => {
                        unit.hex.polygon.classList.remove('availableAttackTarget');
                        unit.hex.polygon.classList.remove('attackTarget');
                    })
                },
                unitMouseoverHandler: hex => {
                    hex.polygon.classList.remove('availableAttackTarget');
                    hex.polygon.classList.add('attackTarget');
                },
                unitMouseoutHandler: hex => {
                    hex.polygon.classList.remove('attackTarget');
                    hex.polygon.classList.add('availableAttackTarget');
                },
                actionHandler: (source, actionSteps) => {
                    console.log('actionSteps:', actionSteps);
                    let target_hex = this.board.grid.hexes[actionSteps[0].target_hex];
                    console.log('hexes:', source.hex, 'and', target_hex);
                    let source_point = source.hex.toPoint();
                    let target_point = target_hex.toPoint();
                    source.image
                        .animate(100, '-', source.animation_delay).move(target_point.x, target_point.y)
                        .animate(100, '-').move(source_point.x, source_point.y);
                    let target = this.board.getUnitByHex(target_hex);
                    if (!!target) {
                        target.getDamage(actionSteps[0].damage);
                    }
                }
            },
            range_attack: {
                set: () => {
                    this.actions.attack.setByAttackHexes(this.board.hero.range_attack_hexes);
                },
                drop: () => {
                    this.actions.attack.drop()
                },
                actionHandler: (source, actionSteps) => {
                    let source_point = source.hex.toPoint();
                    let target_hex = this.board.grid.hexes[actionSteps[0].target_hex];
                    let target_point = target_hex.toPoint();
                    source.range_weapon.move(source_point.x + 30, source_point.y + 30).fill({'opacity': 1})
                        .animate(150).fill({'opacity': 0}).move(target_point.x + 30, target_point.y + 30);
                    target_hex.damage_indicator.text(actionSteps[0].damage.toString());
                    target_hex.damage_indicator
                        .animate(100, '-', source.animation_delay).attr({'opacity': 1})
                        .animate(1000).font({'opacity': 0}).translate(0, -30)
                        .animate(10).translate(0, 0);
                }
            },
//            spells
            path_of_fire: {
                set: () => {
                    this.setTargets(this.board.grid.getHexesInRange(this.board.hero.hex,
                                                                    this.board.hero.spells[this.currentAction].radius,
                                                                    ['empty', 'unit']));
                    this.actionData.path = [];
                },
                drop: () => {
                    this.actionData.path.forEach(_hex => {
                        _hex.polygon.classList.remove('secondaryTarget');
                    });
                },
                mouseover: hex => {
                    let dq = hex.q - this.board.hero.hex.q;
                    let dr = hex.r - this.board.hero.hex.r;
                    for (var i = 1; i < this.board.hero.spells[this.currentAction].path_length + 1; i++) {
                        let current_hex = this.board.grid.getHexByCoords(this.board.hero.hex.q + dq * i,
                                                                         this.board.hero.hex.r + dr * i);
                        if (current_hex === undefined || current_hex.slot == 'obstacle')
                            break;
                        this.actionData.path.push(current_hex);
                        current_hex.polygon.classList.add('secondaryTarget');
                    }
                },
                mouseout: hex => {
                    this.actionData.path.forEach(_hex => {
                        _hex.polygon.classList.remove('secondaryTarget');
                    });
                    this.actionData.path = [];
                },
                hexClickHandler: hex => {
                    this.board.component.requestAction({'action': this.currentAction, 'target_hex': hex.polygon.id});
                },
                unitClickHandler: unit => {
                    this.board.component.requestAction({'action': this.currentAction, 'target_hex': unit.hex.polygon.id});
                },
                actionHandler: (source, actionSteps) => {
                    let animation = anime.timeline({
                        complete: (anim) => {
                            this.animation_elements.clear();
                        }
                    });

                    for (var i = 0; i < actionSteps.length; i++) {
                        let actionStep = actionSteps[i];
                        let hex = this.board.grid.hexes[actionStep.target_hex];
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
                            duration: 200,
                            opacity: 1,
                            scale: 1,
                            translateX: x,
                            translateY: y,
                            easing: 'easeOutQuart'
                        }, 100*i).add({
                            targets: explosion.node,
                            duration: 100,
                            opacity: 0
                        });
                        let unit = this.board.getUnitByHex(hex);
                        if (!!unit) {
                            unit.getDamage(actionStep.damage);
                        }
                    }
                }
            },
            'shield_bash': {
                set: () => {
                    this.setTargets(this.board.grid.getHexesInRange(this.board.hero.hex, 1, ['empty', 'unit', 'obstacle']));
                    this.actionData.hexes_to_bash = [];
                },
                drop: () => {
                    this.actionData.hexes_to_bash.forEach(_hex => {
                        _hex.polygon.classList.remove('secondaryTarget');
                    });
                },
                mouseover: hex => {
                    this.actionData.hexes_to_bash = [];
                    this.board.grid.getHexesInRange(hex, 1).filter(x => this.actionData.target_hexes.includes(x)).forEach(hex_id => {
                        let _hex = this.board.grid.hexes[hex_id];
                        if (this.board.hero.hex != _hex) {
                            this.actionData.hexes_to_bash.push(_hex);
                            _hex.polygon.classList.add('secondaryTarget');
                        }
                    });
                },
                mouseout: hex => {
                    this.actionData.hexes_to_bash.forEach(_hex => {
                        _hex.polygon.classList.remove('secondaryTarget');
                    });
                    this.actionData.hexes_to_bash = [];
                },
                hexClickHandler: hex => {
                    this.board.component.requestAction({'action': this.currentAction, 'target_hex': hex.polygon.id});
                },
                unitClickHandler: unit => {
                    this.board.component.requestAction({'action': this.currentAction, 'target_hex': unit.hex.polygon.id});
                },
                actionHandler: actionData => {
                    const angles = {
                        '1;-1': 60,
                        '1;0': 120,
                        '0;1': 180,
                        '-1;1': 240,
                        '-1;0': 300
                    }
                    let target = actionData.target_hex.split(';');
                    let {x, y} = this.board.hero.hex.toPoint();
                    target[0] -= this.board.hero.hex.q;
                    target[1] -= this.board.hero.hex.r;
                    let angle = angles[target[0] + ';' + target[1]];
                    for (var unit_id in actionData.target_units) {
                        this.board.units[unit_id].getDamage(actionData.target_units[unit_id].damage);
                    }
                    let cone = this.animation_elements.image('./src/assets/bash_wave.png', 60, 60)
                    let animation = anime.timeline({
                        complete: (anim) => {
                            this.animation_elements.clear();
                        }
                    });
                    animation.add({
                        targets: cone.node,
                        duration: 0,
                        delay: 200,
                        opacity: 0.1,
                        translateX: x,
                        translateY: y,
                        easing: 'linear',
                        'transform-origin': '30px 30px',
                        rotate: angle
                    })
                    .add({
                        targets: cone.node,
                        duration: 300,
                        opacity: 0.6,
                        scale: 2.5,
                        easing: 'easeOutExpo'
                    })
                    .add({
                        targets: cone.node,
                        duration: 50,
                        opacity: 0
                    });
                }
            },
            'blink': {
                set: () => {
                    this.setTargets(this.board.grid.getHexesInRange(this.board.hero.hex, 3, ['empty']), false);
                },
                drop: () => {
                },
                mouseover: hex => {
                    hex.polygon.classList.add('secondaryTarget');
                },
                mouseout: hex => {
                    hex.polygon.classList.remove('secondaryTarget');
                },
                hexClickHandler: hex => {
                    this.actionData.destination = hex;
                    this.board.component.requestAction({'action': this.currentAction, 'target_hex': hex.polygon.id});
                    hex.polygon.classList.remove('secondaryTarget');
                },
                actionHandler: actionData => {
                }
            }
        }
    }

    dropCurrentAction() {
        this.actions[this.currentAction].drop();
        this.commonDrop();
        this.actionData = {};
    }

    setAction(actionName) {
        this.currentAction = actionName;
        this.actions[actionName].set();
    }

    changeAction(actionName) {
        if (this.currentAction != actionName) {
            this.dropCurrentAction();
            console.log('Action changed:', this.currentAction, '->', actionName);
            this.setAction(actionName);
        }
    }

    handleAction(actionName, source, actionSteps) {
        if ('actionHandler' in this.actions[actionName]) {
            this.actions[actionName].actionHandler(source, actionSteps);
        }
    }

    commonDrop() {
        if ('target_hexes' in this.actionData) {
            this.actionData.target_hexes.forEach(hex_id => {
                let hex = this.board.grid.hexes[hex_id];
                hex.polygon.classList.remove('spellTarget');
                hex.overTargetHandler = null;
                hex.outTargetHandler = null;
                hex.clickHandler = null;
            });
        }
        if ('target_units' in this.actionData) {
            this.actionData.target_units.forEach(unit => {
                unit.overTargetHandler = null;
                unit.outTargetHandler = null;
                unit.clickTargetHandler = null;
            });
        }
    }

    setTargets(hexes, includeUnits=true) {
        this.actionData.target_hexes = hexes;
        this.actionData.target_hexes.forEach(hex_id => {
            let hex = this.board.grid.hexes[hex_id];
            hex.polygon.classList.add('spellTarget');
            hex.overTargetHandler = this.actions[this.currentAction].mouseover;
            hex.outTargetHandler = this.actions[this.currentAction].mouseout;
            hex.clickHandler = this.actions[this.currentAction].hexClickHandler;
        });
        if (includeUnits) {
            this.actionData.target_units = [];
            for (var unit_id in this.board.units) {
                let unit = this.board.units[unit_id];
                if (this.actionData.target_hexes.includes(unit.hex.q + ';' + unit.hex.r)) {
                    this.actionData.target_units.push(unit);
                    unit.overTargetHandler = this.actions[this.currentAction].mouseover;
                    unit.outTargetHandler = this.actions[this.currentAction].mouseout;
                    unit.clickTargetHandler = this.actions[this.currentAction].unitClickHandler;
                }
            }
        }
    }
}

export default ActionManager
