import anime from 'animejs'
import {Hero} from './game_objects';

class ActionManager {
    constructor(game_instance) {
        this.game_instance = game_instance;
        this.currentAction = null;
        this.actionData = {};
        this.animation_elements = this.game_instance.svg.group();

        this.actions = {
            move: {
                set: () => {
                    this.actionData.path = [];
                    this.game_instance.hero.updateHandler = this.actions.move.heroUpdateHandler;
                    for (var hex_id in this.game_instance.grid.hexes) {
                        this.game_instance.grid.hexes[hex_id].clickHandler = this.actions.move.hexClickHandler;
                    }
                    for (var structure_id in this.game_instance.structures) {
                        this.game_instance.structures[structure_id].clickTargetHandler = this.actions.move.structureClickHandler;
                    }
                    for (var unit_id in this.game_instance.units) {
                        this.game_instance.units[unit_id].clickTargetHandler = this.actions.move.unitClickHandler;
                    }
                },
                drop: () => {
                    this.game_instance.hero.updateHandler = null;
                    this.actions.move.resetPath();
                },
                buildPath: destination => {
                    this.actionData.path = this.game_instance.grid.findPath(this.game_instance.hero.hex, destination);
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
                    if (this.game_instance.grid.distance(hex, this.game_instance.hero.hex) <= this.game_instance.hero.move_range) {
                        this.actions.move.resetPath();
                        this.game_instance.component.requestAction({'action': 'move', 'target_hex': hex.q + ';' + hex.r});
                    } else {
                        this.actions.move.goLongPath(hex);
                    }
                },
                unitClickHandler: unit => {
                    if (this.game_instance.grid.distance(unit.hex, this.game_instance.hero.hex) <= this.game_instance.hero.attack_range) {
                        this.game_instance.component.requestAction({'action': 'attack', 'target_hex': unit.hex.q + ';' + unit.hex.r});
                    } else if (this.game_instance.grid.distance(unit.hex, this.game_instance.hero.hex) <= this.game_instance.hero.attack_range + 1) {
                        this.game_instance.component.requestAction({'action': 'range_attack', 'target_hex': unit.hex.q + ';' + unit.hex.r});
                    } else {
                        this.actions.move.goLongPath(unit.hex);
                    }
                },
                structureClickHandler: structure => {
                    if (this.currentAction != 'move') {
                        this.changeAction('move');
                    }
                    if (this.game_instance.grid.distance(structure.hex, this.game_instance.hero.hex) <= this.game_instance.hero.move_range) {
                        this.actions.move.resetPath();
                        this.game_instance.component.requestAction({'action': structure.code_name,
                                                                    'target_hex': structure.hex.q + ';' + structure.hex.r});
                    } else {
                        this.actions.move.goLongPath(structure.hex);
                    }
                },
                goLongPath: hex => {
                    if ('path' in this.actionData && this.actionData.path.length > 0) {
                        if (hex != this.actionData.path[0]) {
                            this.actions.move.resetPath();
                            this.actions.move.buildPath(hex);
                        } else {
                            let hex_in_path = this.actionData.path[this.actionData.path.length - 1];
                            this.game_instance.component.requestAction({'action': 'move',
                                                                'target_hex': hex_in_path.q + ';' + hex_in_path.r});
                        }
                    } else {
                        this.actions.move.buildPath(hex);
                    }
                },
                actionHandler: (source, actionSteps) => {
                    let target_hex = this.game_instance.grid.hexes[actionSteps[0].target_hex];
                    source.move(target_hex);
                    if (source instanceof Hero && 'path' in this.actionData && this.actionData.path.length > 0) {
                        let passed_hex = this.actionData.path.pop(this.actionData.path.length - 1);
                        passed_hex.polygon.classList.remove('path');
                    }
                }
            },
            attack: {
                set: () => {
                    this.actions.attack.setByAttackHexes(this.game_instance.hero.attack_hexes);
                },
                setByAttackHexes: attackHexes => {
                    this.actionData.target_units = [];
                    for (var unit_id in this.game_instance.units) {
                        let unit = this.game_instance.units[unit_id];
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
                    let target_hex = this.game_instance.grid.hexes[actionSteps[0].target_hex];
                    let source_point = source.hex.toPoint();
                    let target_point = target_hex.toPoint();
                    source.image
                        .animate(100, '-', source.animation_delay).move(target_point.x, target_point.y)
                        .animate(100, '-').move(source_point.x, source_point.y);
                    if ('damage' in actionSteps[0]) {
                        let target = this.game_instance.getUnitByHex(target_hex);
                        if (!!target) {
                            target.getDamage(actionSteps[0].damage);
                        }
                    }
                }
            },
            range_attack: {
                set: () => {
                    this.actions.attack.setByAttackHexes(this.game_instance.hero.range_attack_hexes);
                },
                drop: () => {
                    this.actions.attack.drop()
                },
                actionHandler: (source, actionSteps) => {
                    let source_point = source.hex.toPoint();
                    let target_hex = this.game_instance.grid.hexes[actionSteps[0].target_hex];
                    let target_point = target_hex.toPoint();
                    source.range_weapon.move(source_point.x + 30, source_point.y + 30).fill({'opacity': 1})
                        .animate(150).fill({'opacity': 0}).move(target_point.x + 30, target_point.y + 30);
                    if ('damage' in actionSteps[0]) {
                        let target = this.game_instance.getUnitByHex(target_hex);
                        if (!!target) {
                            target.getDamage(actionSteps[0].damage);
                        }
                    }
                }
            },
//            spells
            path_of_fire: {
                set: () => {
                    this.setTargets(this.game_instance.grid.getHexesInRange(this.game_instance.hero.hex,
                                                                    this.game_instance.hero.spells[this.currentAction].radius,
                                                                    ['empty', 'unit']));
                    this.actionData.path = [];
                },
                drop: () => {
                    this.actionData.path.forEach(_hex => {
                        _hex.polygon.classList.remove('secondaryTarget');
                    });
                },
                mouseover: hex => {
                    let dq = hex.q - this.game_instance.hero.hex.q;
                    let dr = hex.r - this.game_instance.hero.hex.r;
                    for (var i = 1; i < this.game_instance.hero.spells[this.currentAction].path_length + 1; i++) {
                        let current_hex = this.game_instance.grid.getHexByCoords(this.game_instance.hero.hex.q + dq * i,
                                                                         this.game_instance.hero.hex.r + dr * i);
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
                    this.game_instance.component.requestAction({'action': this.currentAction, 'target_hex': hex.polygon.id});
                },
                unitClickHandler: unit => {
                    this.game_instance.component.requestAction({'action': this.currentAction, 'target_hex': unit.hex.polygon.id});
                },
                actionHandler: (source, actionSteps) => {
                    let animation = anime.timeline({
                        complete: (anim) => {
                            this.animation_elements.clear();
                        }
                    });

                    for (var i = 0; i < actionSteps.length; i++) {
                        let actionStep = actionSteps[i];
                        let hex = this.game_instance.grid.hexes[actionStep.target_hex];
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
                        if ('damage' in actionStep) {
                            let unit = this.game_instance.getUnitByHex(hex);
                            if (!!unit) {
                                unit.getDamage(actionStep.damage);
                            }
                        }
                    }
                }
            },
            shield_bash: {
                set: () => {
                    this.setTargets(this.game_instance.grid.getHexesInRange(this.game_instance.hero.hex, 1, ['empty', 'unit', 'obstacle']));
                    this.actionData.hexes_to_bash = [];
                },
                drop: () => {
                    this.actionData.hexes_to_bash.forEach(_hex => {
                        _hex.polygon.classList.remove('secondaryTarget');
                    });
                },
                mouseover: hex => {
                    this.actionData.hexes_to_bash = [];
                    this.game_instance.grid.getHexesInRange(hex, 1).filter(x => this.actionData.target_hexes.includes(x)).forEach(hex_id => {
                        let _hex = this.game_instance.grid.hexes[hex_id];
                        if (this.game_instance.hero.hex != _hex) {
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
                    this.game_instance.component.requestAction({'action': this.currentAction, 'target_hex': hex.polygon.id});
                },
                unitClickHandler: unit => {
                    this.game_instance.component.requestAction({'action': this.currentAction, 'target_hex': unit.hex.polygon.id});
                },
                actionHandler: (source, actionSteps) => {
                    const angles = {
                        '1;-1': 60,
                        '1;0': 120,
                        '0;1': 180,
                        '-1;1': 240,
                        '-1;0': 300
                    }
                    let main_target = null;
                    for (var i = 0; i < actionSteps.length; i++) {
                        let actionStep = actionSteps[i];
                        let _hex = this.game_instance.grid.hexes[actionStep.target_hex];
                        let unit = this.game_instance.getUnitByHex(_hex);
                        if (!!unit) {
                            unit.getDamage(actionStep.damage);
                            if (!!actionStep.pushed_to) {
                                unit.move(this.game_instance.grid.hexes[actionStep.pushed_to]);
                            }
                        }
                        if (actionStep.main_target == true) {
                            main_target = actionStep.target_hex;
                        }
                    }

                    let target = main_target.split(';');
                    let {x, y} = source.hex.toPoint();
                    target[0] -= source.hex.q;
                    target[1] -= source.hex.r;
                    let angle = angles[target[0] + ';' + target[1]];
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
            blink: {
                set: () => {
                    this.setTargets(this.game_instance.grid.getHexesInRange(this.game_instance.hero.hex, 3, ['empty']), false);
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
                    this.game_instance.component.requestAction({'action': this.currentAction, 'target_hex': hex.polygon.id});
                    hex.polygon.classList.remove('secondaryTarget');
                },
                actionHandler: (source, actionSteps) => {
                    let target_hex = this.game_instance.grid.hexes[actionSteps[0].target_hex];
                    source.move(target_hex, 10);
                }
            },
            sanctuary: {
                actionHandler: (source, actionsSteps) => {
                    let assortment = actionsSteps[0].assortment;
                    this.game_instance.structures['sanctuary'].open(assortment);
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
                let hex = this.game_instance.grid.hexes[hex_id];
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
            let hex = this.game_instance.grid.hexes[hex_id];
            hex.polygon.classList.add('spellTarget');
            hex.overTargetHandler = this.actions[this.currentAction].mouseover;
            hex.outTargetHandler = this.actions[this.currentAction].mouseout;
            hex.clickHandler = this.actions[this.currentAction].hexClickHandler;
        });
        if (includeUnits) {
            this.actionData.target_units = [];
            for (var unit_id in this.game_instance.units) {
                let unit = this.game_instance.units[unit_id];
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
